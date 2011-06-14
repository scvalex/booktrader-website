from booksexchange.views.common import *


@view_config(context=Books, name='search', renderer='books/search.mak')
def search(context, request):
    if 'Search' not in request.params:
        raise HTTPBadRequest('No search.')

    class BooksSchema(colander.SequenceSchema):
        book = BookSchema()

    class ResultSchema(colander.MappingSchema):
        items = BooksSchema(missing=[])
        totalItems = colander.SchemaNode(colander.Integer())

    query = request.params.items()

    search_form = deform.Form(SearchSchema(), buttons=('Search',))

    try:
        query = search_form.validate(query)
    except deform.ValidationFailure, e:
        # This basically means that there is no query
        redir = request.referer and request.referer or '/'
        raise HTTPFound(location = redir)

    search_form.schema['query'].default = query['query']
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
    words = query['query'].lower().split()

    owned_books = []

    for word in words:
        try:
            res = context.query(Contains('title', word) |
                                Contains('subtitle', word))[1]
            owned_books.extend(res)
        except ParseError:
            pass

    # Compute -3 and +3 page indices around the current page
    page_indices = start_index / books_per_page - 3
    if page_indices < 0:
        page_indices = 0
    num_items = 7
    if page_indices + num_items > total_items / books_per_page:
        num_items = total_items / books_per_page - page_indices
    page_indices = range(page_indices, page_indices + num_items + 1)

    return {'total_items': total_items,
            'google_books': google_books,
            'page_indices': page_indices,
            'page_index': start_index / books_per_page,
            'books_per_page': books_per_page,
            'owned_books': owned_books}

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
