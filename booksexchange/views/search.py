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
from booksexchange.views.book   import search_books

@view_config(context=App, name='search')
def search(context, request):
    if 'Search' not in request.params:
        raise HTTPBadRequest('No search.')

    query = request.params.items()

    search_form = deform.Form(SearchSchema(), buttons=('Search',))

    try:
        query = search_form.validate(query)
    except deform.ValidationFailure, e:
        # This basically means that there is no query
        redir = request.referer and request.referer or '/'
        raise HTTPFound(location = redir)

    
    search_form.schema['query'].default = query['query']

    if query['type'] == 'books':
        return search_books(context['books'], request, query)
    else:
        raise Exception()
    

