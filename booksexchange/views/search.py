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

from booksexchange.views.common import *
from booksexchange.views.book   import search_books, search_books_groups

@view_config(context=App, name='search', renderer='search.mak')
def search(context, request):
    if 'Search' not in request.params:
        raise HTTPBadRequest('No search.')

    query = request.params.items()

    search_form = deform.Form(SearchSchema(), buttons=('Search',))

    try:
        query = search_form.validate(query)
    except deform.ValidationFailure, e:
        # This basically means that there is no query
        redir = request.referer and request.referer or base_url(request)
        raise HTTPFound(location = redir)

    request.session['last_search'] = query['query']

    if query['type'] == 'books':
        return search_books(context['books'], request, query, request.GET)

    qs = query['query'].lower()

    try:
        if query['type'] == 'users':
            (count, items) = context['users'].query(Contains('username', qs))
            t = 'users'
        elif query['type'] == 'groups':
            (count, items) = context['groups'].query(Contains('name', qs) |
                                                     Contains('description', qs))
            t = 'groups'
        elif query['type'] == 'group_books':
            if request.user:
                items = search_books_groups(context['books'], request, query)
            else:
                return {'error': "You can't search for books in the same groups if you're not logged in."}
    except ParseError, e:
        return {'error': e.message}

    return {'items': [i for i in items],
            'search_type':  query['type'],
            'error' : None}

@view_config(context=App, name='autocomplete', renderer='json')
def autocomplete(context, request):
    if 'term' not in request.GET:
        raise HTTPBadRequest('No term specified')

    term = request.GET['term']


    if len(request.subpath) != 1:
        raise HTTPBadRequest('No search type specified')

    search_type = request.subpath[0]

    if search_type == 'books':
        conn = httplib.HTTPConnection(request.registry.settings['google_autocomplete'])
        conn.request('GET', request.registry.settings['google_query'] % term)

        data = conn.getresponse().read()

        # Removing the function
        data = json.loads(data[data.find('['):-1])
        
        data = map(lambda x: x[0], data[1])
        
        return data
    elif search_type == 'users':
        count, res = context['users'].query(Contains('ac_username', term.lower()),
                                            limit=10)
        return [u.username for u in res]
    elif search_type == 'groups':
        count, res = context['groups'].query(Contains('ac_name', term.lower()),
                                             limit=10)
        return [g.name for g in res]
    else:
        raise HTTPBadRequest('Bad search type.')
    
