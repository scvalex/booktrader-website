from pyramid.view           import view_config
from pyramid.url            import resource_url
from pyramid.traversal      import resource_path
from pyramid.exceptions     import Forbidden
from pyramid.security       import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPInternalServerError, HTTPBadRequest

from repoze.catalog.query   import Eq

import colander
import deform
import json

from booksexchange.models   import App, Users, User, Books, Book


@view_config(context=App, renderer='home.mak')
def home(context, request):
    return {'blah': 'bloh'}

@view_config(context=Users, renderer='users.mak')
def view_users(context, request):
    return {'users': list(context)}


@view_config(context=Forbidden)
def forbidden(request):
    if authenticated_userid(request):
        return HTTPForbidden()
    
    return HTTPFound(location = resource_path(request.root['users'], 'login'))


def already_logged_in(request):
    # If the user is logged in already, redirect
    if authenticated_userid(request):
        request.session.flash('You are already logged in.')
        return True
    
    return False
    
@view_config(context=Users, name='login', renderer='users/login.mak')
def login(context, request):

    if already_logged_in(request):
        return HTTPFound(location = '/')

    referrer  = request.url
    
    if referrer == request.path_url:
        referrer = '/'

    came_from = request.params.get('came_from', referrer)

    username = ''

    # If the request is post, try to authenticate
    if 'form.submitted' in request.params:
        username = request.params['username']
        password = request.params['password']

        if username in context and context[username].check_password(password):
            headers = remember(request, username)
            return HTTPFound(location = came_from,
                             headers  = headers)

        request.session.flash('Invalid username/password.')

    
    return dict(came_from = came_from,
                username  = username)

@view_config(context=Users, name='logout')
def logout(context, request):
    headers = forget(request)
    return HTTPFound(location = resource_url(context, request),
                     headers = headers)


@view_config(context=Users, name='register', renderer='users/register.mak')
def register(context, request):

    if already_logged_in(request):
        return HTTPFound(location = '/')

    def validate_user(node, value):
        colander.Length(min=5, max=200)(node, value)

        if context.query(Eq('username', value))[0] != 0:
            raise colander.Invalid(node, '"' + value + '" is already taken.')
    
    def validate_email(node, value):
        colander.Email()(node, value)

        if context.query(Eq('email', value))[0] != 0:
            raise colander.Invalid(node, 'The email you inserted is already present.')

    class RegisterSchema(colander.Schema):
        username = colander.SchemaNode(colander.String(),
                                       validator = validate_user)
        password = colander.SchemaNode(colander.String(),
                                       validator = colander.Length(min=5, max=100),
                                       widget    = deform.widget.CheckedPasswordWidget(size=20))
        email    = colander.SchemaNode(colander.String(),
                                       validator = validate_email)
        

    schema = RegisterSchema()
    form   = deform.Form(schema, buttons=('Register',))

    if 'Register' in request.params:
        controls = request.params.items()

        try:
            register_data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        new_user = User(register_data['username'],
                        register_data['email'],
                        register_data['password'])
        
        context.new_user(new_user)

        request.session.flash('Your registration was successfull, enjoy BooksExchange!')

        return HTTPFound(location = '/',
                         headers  = remember(request, new_user.username))
    
    return {'form': form.render()}

@view_config(context=Books, name='search', renderer='books/search.mak')
def search(context, request):
    utf8_string = lambda: colander.String(encoding="utf-8")

    class SearchSchema(colander.Schema):
        query = colander.SchemaNode(utf8_string())

    class AuthorsSchema(colander.SequenceSchema):
        author = colander.SchemaNode(utf8_string())

    class IndustryIdentifierSchema(colander.MappingSchema):
        type       = colander.SchemaNode(utf8_string(), name = "type")
        identifier = colander.SchemaNode(utf8_string())

    class IndustryIdentifiersSchema(colander.SequenceSchema):
        identifier = IndustryIdentifierSchema()

    class VolumeInfoSchema(colander.MappingSchema):
        title       = colander.SchemaNode(utf8_string())
        subtitle    = colander.SchemaNode(utf8_string(), missing="")
        authors     = AuthorsSchema(missing=[])
        publisher   = colander.SchemaNode(utf8_string(), missing="")
        industryIdentifiers = IndustryIdentifiersSchema()
        description = colander.SchemaNode(utf8_string(), missing="")
        publishedDate = colander.SchemaNode(utf8_string(), missing="")

    class BookSchema(colander.MappingSchema):
        volumeInfo = VolumeInfoSchema()

    class BooksSchema(colander.SequenceSchema):
        book = BookSchema()

    class ResultSchema(colander.MappingSchema):
        items = BooksSchema()

    search_form = deform.Form(SearchSchema(), buttons=('Search',))

    if 'Search' in request.POST:
        query = request.POST.items()

        try:
            query = search_form.validate(query)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        rsp = context.catalogue.query(query['query'])
        if not rsp:
            raise HTTPBadRequest("no query parameter")

        books = json.load(rsp)
        try:
            books = ResultSchema().deserialize(books)
        except colander.Invalid, e:
            raise HTTPInternalServerError(str(e.asdict()) + str(books))

        def book_to_book(b):
            b = b['volumeInfo']
            authors =b['authors']
            identifiers = [[i['type'], i['identifier']]
                           for i in b['industryIdentifiers']]
            return Book(b['title'], b['subtitle'], authors, b['publisher'],
                        b['publishedDate'], identifiers, b['description'])

        books = [book_to_book(vi) for vi in books['items']]

        return {'form': search_form.render(),
                'result': books}

    return {'form': search_form.render(),
            'result': []}
