from pyramid.view           import view_config
from pyramid.traversal      import resource_path
from pyramid.exceptions     import Forbidden
from pyramid.security       import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPInternalServerError, HTTPBadRequest

from repoze.catalog.query   import Eq

import colander
import deform
import json

from booksexchange.models   import App, Users, User, Books, Book
from booksexchange.schemas  import SearchSchema, utf8_string
from booksexchange.utils    import send_email


@view_config(context=App, renderer='home.mak')
def home(context, request):
    return {'blah': 'bloh'}


@view_config(context=Users, renderer='users.mak', permission='loggedin')
def view_users(context, request):
    return {'users': list(context)}


@view_config(context=Forbidden)
def forbidden(request):
    if authenticated_userid(request):
        return HTTPForbidden()

    return HTTPFound(location = resource_path(request.root['users'], 'login',
                                              *request.path.split('/')))


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

    referer = request.referer

    if not referer:
        # because redirecting with HTTPFound foobars the referer header
        referer = '/' + '/'.join(request.path_info.split('/')[3:])

    if referer == request.path_url:
        referer = '/'

    came_from = request.params.get('came_from', referer)

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

    
    return {'came_from' : came_from,
            'username' : username}

@view_config(context=Users, name='logout', permission='loggedin')
def logout(context, request):
    headers = forget(request)

    referrer = request.url

    if referrer == request.path_url:
        referrer = '/'

    request.session.flash('You are now logged out.')
    
    return HTTPFound(location = referrer,
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
        password = colander.SchemaNode(
            colander.String(),
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

        return HTTPFound(location = request.resource_url(new_user, 'generate_token'))
    
    return {'form': form.render()}
                         

@view_config(context=User, name='generate_token',
             renderer='users/generate_token.mak')
def generate_token(context, request):
    token = context.generate_token()

    confirm_url = request.resource_url(context, 'confirm',
                                       query = {'token': token})
    
    email_body = "Dear " + context.username + ",\n\n" + \
                 "To activate your account " + \
                 "please click visit this link: " + confirm_url + ".\n\n" + \
                 "The BooksExchange team."


    send_email(email_body, 'BooksExchange account activation.',
               [context.email], request.registry.settings)

    return {'wrong_token': ('wrong' in request.params)}
                         

@view_config(context=User, name='confirm')
def confirm_user(context, request):
    if not 'token' in request.params or context.confirmed:
        print request.resource_url(context, 'confirm')
        return Forbidden()

    token = request.params['token']

    if context.confirm(token):
        request.session.flash('Your accound was verified, enjoy BooksExchange!')

        return HTTPFound(location = '/',
                         headers  = remember(request, context.username))

    return HTTPFound(location = request.resource_url(context,
                                                     'generate_token',
                                                     query = {'wrong':True}))


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
    id         = colander.SchemaNode(utf8_string())
    volumeInfo = VolumeInfoSchema()


def json_to_book(b):
    id = b['id']
    b = b['volumeInfo']
    authors =b['authors']
    identifiers = [[i['type'], i['identifier']]
                   for i in b['industryIdentifiers']]
    book = Book(b['title'], b['subtitle'], authors, b['publisher'],
                b['publishedDate'], identifiers, b['description'])
    book.googleId = id
    return book


@view_config(context=Books, name='search', renderer='books/search.mak')
def search(context, request):
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
            return HTTPInternalServerError("no response from catalogue")

        books = json.load(rsp)
        try:
            books = ResultSchema().deserialize(books)
        except colander.Invalid, e:
            return HTTPInternalServerError(str(e.asdict()) + str(books))

        books = [json_to_book(vi) for vi in books['items']]

        return {'form': search_form.render(),
                'result': books}

    return {'form': search_form.render(),
            'result': []}


@view_config(context=Books, name='add', permission='loggedin')
def add_book(context, request):
    id = request.path.split('/')[-1]    # probably a bad idea

    if id:
        book = context.catalogue.volume(id)
        if not book:
            raise HTTPInternalServerError("no responese from catalogue")

        book = json.load(book)
        try:
            book = BookSchema().deserialize(book)
        except colander.Invalid, e:
            raise HTTPInternalServerError(str(e.asdict()) + str(book))

        book = json_to_book(book)

        user = request.user
        if user is None:
            raise HTTPInternalServerError("no user found")

        if book.identifier in user.owned:
            raise HTTPBadRequest("book already owned")

        context.new_book(book)
        user.add_book(book)

        request.session.flash('Book added!')
        return HTTPFound(location = request.resource_url(context, 'list'))

    return HTTPBadRequest("no book specified")


@view_config(context=Books, name='list', renderer='books/list.mak',
             permission='loggedin')
def list_book(context, request):
    user = authenticated_userid(request)
    user = request.root['users'][user]
    if not user:
        raise HTTPInternalServerError("no user found")

    books = user.owned.itervalues()

    return {'books': books}
