# Copyright 2011 the authors of BookTrader (see the AUTHORS file included).
#
# This file is part of BookTrader.
#
# BookTrader is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 of the License.
#
# BookTrader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even any implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License version 3 for more details.
#
# You should have received a copy of the GNU Affero General Public
# License version 3 along with BookTrader. If not, see:
# http://www.gnu.org/licenses/

from email                   import Header
from email.mime.text         import MIMEText

from mako.template           import Template

from pyramid.decorator       import reify
from pyramid.httpexceptions  import HTTPException, HTTPInternalServerError, HTTPFound, HTTPBadRequest
from pyramid.mako_templating import renderer_factory as mako_renderer_factory
from pyramid.request         import Request
from pyramid.response        import Response
from pyramid.security        import unauthenticated_userid
from pyramid.traversal       import resource_path, find_resource, find_root

from persistent.list         import PersistentList
from persistent.mapping      import PersistentMapping

from repoze.catalog.catalog  import Catalog
from repoze.catalog.document import DocumentMap
from repoze.folder           import Folder

from urllib                  import urlencode
from urllib2                 import urlopen, URLError

from webhelpers.html.builder import literal

from webob.dec               import wsgify

import datetime
import deform
import json
import markdown
import smtplib

from booksexchange.schemas   import SearchSchema

class AppRequest(Request):
    @reify
    def user(self):
        userid = unauthenticated_userid(self)

        if userid is not None and userid in self.root['users']:
            return self.root['users'][userid]

        return None

    @reify
    def search_bar(self):
        action = self.resource_url(self.root, 'search')
        return deform.Form(SearchSchema(),
                           buttons = ('Search',),
                           action  = action,
                           formid  = 'search_bar',
                           method  = 'GET').render()

    def markdown(self, text):
        return literal('<div class="md">' +
                       markdown.markdown(text) +
                       '</div>')


def json_request(request):
    return request.params.get('format', 'html') == 'json'

class AppEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PersistentList):
            return obj.data
        if isinstance(obj, PersistentMapping):
            return obj.data
        if hasattr(obj, '__dict__'):
            if (callable(obj.__dict__)):
                return obj.__dict__()
            return obj.__dict__
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def app_renderer_factory(info):
    def render(value, system):
        request = system['request']

        if json_request(request):
            request.response_content_type = 'application/json'
            value['status'] = 'ok'
            return json.dumps(value, cls=AppEncoder)

        return mako_renderer_factory(info)(value, system)

    return render

class IndexFolder(Folder):
    def __init__(self, **kwargs):
        super(IndexFolder, self).__init__()

        self._docmap = DocumentMap()

        self._catalog = Catalog()

        for k, v in kwargs.iteritems():
            self._catalog[k] = v

    def __setitem__(self, name, obj):
        self.add(name, obj)

    def __delitem__(self, name):
        self.remove(name)

    def add(self, name, obj, *args, **kwargs):
        super(IndexFolder, self).add(name, obj, *args, **kwargs)

        docid = self._docmap.add(resource_path(obj))
        self._catalog.index_doc(docid, obj)

    def remove(self, name, *args, **kwargs):
        obj = self[name]

        docid = self._docmap.docid_for_address(resource_path(obj))
        self._docmap.remove_docid(docid)
        self._catalog.unindex_doc(docid)

        super(IndexFolder, self).remove(name, *args, **kwargs)

    def query(self, *args, **kwargs):
        res   = self._catalog.query(*args, **kwargs)

        items = (find_resource(find_root(self), self._docmap.address_for_docid(index))
                 for index in res[1])
        return (res[0], items)

    def update(self, obj):
        self._catalog.reindex_doc(self._docmap.docid_for_address(resource_path(obj)),
                                  obj)


def send_email(body, subject, recipients, settings, sender=None):
    """
    Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.

    Thanks to http://mg.pov.lt/blog/unicode-emails-in-python for the
    encoding tips.
    """

    # Fallback to default sender
    if not sender:
        sender = settings['smtp_email']

    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    # Make sure email addresses do not contain non-ASCII characters
    sender = sender.encode('ascii')
    recipients = [recipient.encode('ascii') for recipient in recipients]

    # Sends the email through SSL
    msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
    msg['Subject'] = subject.encode('ascii')
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    server = smtplib.SMTP_SSL(settings['smtp_server'], settings['smtp_port'])
    server.login(settings['smtp_username'], settings['smtp_password'])
    server.sendmail(sender, recipients, msg.as_string())

    server.quit()


class CatalogueException(RuntimeError):
    def __init__(self, str, url):
        super(CatalogueException, self).__init__(str)
        self.url = url

    def __str__(self):
        return super(CatalogueException, self).__str__() + ": " + self.url

class GoogleBooksCatalogue(object):
    key = 'AIzaSyCwMw-h8bLntjsRydO8AXjwinfD5HnGpz4' # scvalex
    base_url = 'https://www.googleapis.com/books/v1'

    def query(self, qstr, start_index = 0, limit = 10):
        url = "%s/volumes?%s" % (GoogleBooksCatalogue.base_url,
                                 urlencode({"q": qstr, "key": self.key,
                                            "startIndex": start_index,
                                            "maxResults": limit}))
        try:
            return urlopen(url, timeout=10)
        except URLError, e:
            raise CatalogueException(str(e), url = url)

    def volume(self, id):
        url = "%s/volumes/%s?%s" % (GoogleBooksCatalogue.base_url, id,
                                    urlencode({"key": self.key}))
        try:
            return urlopen(url, timeout=10)
        except URLError, e:
            raise CatalogueException(str(e), url = url)

@wsgify.middleware
def catch_exc(req, app):
    try:
        return req.get_response(app)
    except HTTPInternalServerError:
        raise
    except HTTPException as e:
        status = e.status

        if json_request(req):
            if isinstance(e, HTTPFound):
                resp = json.dumps({'status': 'ok'})
                status = 200
            else:
                resp = json.dumps({'status': 'error', 'reason': str(e)})
        else:
            if isinstance(e, HTTPBadRequest):
                #req.session.flash('Offer accepted!')
                headers = e.headers
                if req.referer is not None:
                    headers['Location'] = req.referer
                else:
                    headers['Location'] = '/'
                return Response(body='bad request', status=302, headers=headers)

            resp = Template(filename = "booksexchange/templates/exception.mak")
            resp = resp.render(**{'status': e.status, 'detail': e.detail})

        headers = e.headers
        if 'Content-Length' in headers:
            del headers['Content-Length']

        return Response(body=resp, status=status, headers=headers)

def substrings(s):
    res = [s]
    length = len(s)

    if length < 4:
        return res
    
    res.extend([s[:i] for i in range(3, length)])
    res.extend([s[i:] for i in range(1, length - 2)])
    res.extend([s[i:length-i] for i in range(1, (length-1)//2)])
    return res
