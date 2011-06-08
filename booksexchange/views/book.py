from booksexchange.views.common import *


@view_config(context=Books, name='search', renderer='books/search.mak')
def search(context, request):
    class BooksSchema(colander.SequenceSchema):
        book = BookSchema()

    class ResultSchema(colander.MappingSchema):
        items = BooksSchema(missing=[])
        totalItems = colander.SchemaNode(colander.Integer())

    def json_response(obj):
        return Response(body = json.dumps(obj),
                        content_type = "text/json")

    def json_book(book):
        return {"title": book.title,
                "subtitle": book.subtitle,
                "authors": book.authors,
                "publisher": book.publisher,
                "thumbnail": book.image_links['thumbnail'],
                "smallThumbnail": book.image_links['smallThumbnail']}

    query = request.params.items()

    json_query = dict(query).get("format", "html") == "json"

    if 'Search' in request.params:
        search_form = deform.Form(SearchSchema(), buttons=('Search',))

        try:
            query = search_form.validate(query)
        except deform.ValidationFailure, e:
            if json_query:
                return json_response({"status": "error",
                                      "reason": "invalid fields"})
            return {'form': e.render()}

        search_form.schema['query'].default = query['query']
        start_index = query['start_index']

        try:
            rsp = request.root['cache'].get(request.path_qs, lambda: context.catalogue.query(query['query'], start_index).read())
        except CatalogueException, e:
            raise HTTPInternalServerError("no response from catalogue: " +
                                          str(e))

        books = json.loads(rsp)
        try:
            books = ResultSchema().deserialize(books)
        except colander.Invalid, e:
            raise HTTPInternalServerError(str(e.asdict()) + str(books))

        total_items = books['totalItems']
        books = [context.json_to_book(vi) for vi in books['items']]


        def make_url(i):
            return re.sub("start_index=(" + str(start_index) + ")?",
                          "start_index=" + str(i * 10),
                          request.url)

        prev_url = ""
        if start_index > 0:
            prev_url = make_url(start_index / 10 - 1)
        next_url = ""
        if start_index < total_items:
            next_url = make_url(start_index / 10 + 1)

        # Compute -3 and +3 page indices around the current page
        page_indices = start_index / 10 - 3
        if page_indices < 0:
            page_indices = 0
        num_items = 7
        if page_indices + num_items > total_items / 10:
            num_items = total_items / 10 - page_indices
        page_indices = range(page_indices, page_indices + num_items)

        if json_query:
            return json_response({"status": "ok",
                                  "total_items": total_items,
                                  "result": [json_book(b) for b in books]})
        return {'form': search_form.render(),
                'total_items': total_items, 'result': books,
                'page_indices': page_indices, 'page_index': start_index / 10,
                'make_url': make_url,
                'next_url': next_url, 'prev_url': prev_url}

    if json_query:
        return json_response({"status": "error",
                              "reason": "missing parameters"})
    return {'result': None}

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
    if user is None:
        raise HTTPInternalServerError('no user found')

    if kind == 'have' and book.identifier in user.owned:
        raise HTTPBadRequest('book already owned')
    elif kind == 'want' and book.identifier in user.want:
        raise HTTPBadRequest('book already wanted')

    if book.identifier not in request.root['books']:
        request.root['books'].new_book(book)
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

    request.session.flash('Book added!')
    raise HTTPFound(location = request.referer)

@view_config(context=Book, name='remove', permission='loggedin')
def remove_book(context, request):
    if not request.user.remove_book(context) or not context.remove_user(request.user):
        raise HTTPBadRequest('bad jojo')

    request.session.flash('Book removed!')
    raise HTTPFound(location = request.referer)
