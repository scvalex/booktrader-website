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


def search_books(context, request, query):
    class BooksSchema(colander.SequenceSchema):
        book = BookSchema()

    class ResultSchema(colander.MappingSchema):
        items = BooksSchema(missing=[])
        totalItems = colander.SchemaNode(colander.Integer())

    start_index = query['start_index']

    ###########################################################################
    # Google results
    try:
        rsp = request.root['cache'].get(
            request.path_qs,
            lambda: context.catalogue.query(query['query'], start_index,
                                            query['limit']).read())
    except CatalogueException, e:
        raise HTTPInternalServerError("no response from catalogue: " +
                                      str(e))

    books_per_page = query['limit']

    google_books = json.loads(rsp)
    try:
        google_books = ResultSchema().deserialize(google_books)
    except colander.Invalid, e:
        raise HTTPInternalServerError(str(e.asdict()) + str(google_books))

    total_items = google_books['totalItems']
    google_books = [context.json_to_book(vi) for vi in google_books['items']]

    ###########################################################################
    # Internal results
    words = query['query'].lower()

    owned_books = [b for b in context.query(Contains('title', words) |
                                            Contains('subtitle', words))[1]]

    # Compute -3 and +3 page indices around the current page
    page_indices = start_index / books_per_page - 3
    if page_indices < 0:
        page_indices = 0
    num_items = 7
    if page_indices + num_items > total_items / books_per_page:
        num_items = total_items / books_per_page - page_indices
    page_indices = range(page_indices, page_indices + num_items + 1)

    value = {'total_items': total_items,
             'google_books': google_books,
             'page_indices': page_indices,
             'page_index': start_index / books_per_page,
             'books_per_page': books_per_page,
             'owned_books': owned_books}
    return render_to_response('books/search.mak', value, request=request)

@view_config(context=Book, renderer='books/details.mak')
def view_book(context, request):
    return {'book': context}


@view_config(context=Book, name='have', permission='loggedin')
@view_config(context=Book, name='want', permission='loggedin')
def add_book(book, request):
    kind = request.view_name
    if not (kind in ['have', 'want']):
        raise HTTPBadRequest("must add to either 'have' or 'want'")

    user = request.user

    if kind == 'have' and book.identifier in user.owned:
        raise HTTPBadRequest('book already owned')
    elif kind == 'want' and book.identifier in user.want:
        raise HTTPBadRequest('book already wanted')

    if kind == 'have':
        request.user.remove_book(book) # don't want it anymore
        book.remove_user(request.user)
        user.add_owned(book)
        book.add_owner(user)
        request.root['events'].add_have(user, book)
    else:
        user.add_want(book)
        book.add_coveter(user)
        request.root['events'].add_want(user, book)

    if book.identifier not in request.root['books']:
        request.root['books'].new_book(book)

    request.session.flash('Book added!')

    referer = request.referer
    if 'ref' in request.params:
        referer = request.params['ref']
    if referer == request.path:
        referer = '/'
    raise HTTPFound(location = referer)

@view_config(context=Book, name='remove', permission='loggedin')
def remove_book(context, request):
    if not request.user.remove_book(context) or not context.remove_user(request.user):
        raise HTTPBadRequest('bad jojo')

    request.session.flash('Book removed!')

    if request.referer:
        raise HTTPFound(location = request.referer)
    else:
        raise HTTPFound(location = '/')
