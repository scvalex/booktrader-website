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

from pyramid.exceptions        import Forbidden
from pyramid.httpexceptions    import (HTTPFound, HTTPForbidden,
                                       HTTPException, HTTPRedirection,
                                       HTTPInternalServerError, HTTPBadRequest,
                                       HTTPNotFound)
from pyramid.response          import Response
from pyramid.security          import remember, forget, authenticated_userid
from pyramid.traversal         import resource_path
from pyramid.view              import view_config
from pyramid.renderers         import render_to_response

from repoze.catalog.query      import Eq, Contains, And

from zope.index.text.parsetree import ParseError

import colander
import deform
import json
import re
import urllib

from booksexchange.models      import *
from booksexchange.schemas     import *
from booksexchange.utils       import send_email, CatalogueException, json_request


@view_config(context=App, renderer='home.mak')
def home(context, request):
    return {'events': context['events']}


@view_config(context=Forbidden)
def forbidden(request):
    if authenticated_userid(request):
        raise HTTPForbidden("You don't have enough permissions to access this page.")

    if json_request(request):
        raise HTTPForbidden("Get more permissions!!!")

    raise HTTPFound(location = request.resource_url(request.root['users'], 'login',
                                                    query={'ref':request.path}))
