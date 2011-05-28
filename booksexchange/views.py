from pyramid.view           import view_config
from pyramid.traversal      import resource_path
from pyramid.exceptions     import Forbidden
from pyramid.security       import remember, forget, authenticated_userid
from pyramid.httpexceptions import (HTTPFound, HTTPForbidden,
                                    HTTPInternalServerError, HTTPBadRequest,
                                    HTTPException, HTTPRedirection)

from repoze.catalog.query   import Eq

import colander
import deform
import json

from booksexchange.models   import App, Users, User, Books, Book
from booksexchange.schemas  import *
from booksexchange.utils    import send_email, CatalogueException



@view_config(context=HTTPException, renderer='exception.mak')
def httpexception(context, request):
    return {'status': context.status,
            'detail': context.detail}


@view_config(context=HTTPRedirection)
def httpexception(context, request):
    return context


@view_config(context=App, renderer='home.mak')
def home(context, request):
    return {'blah': 'bloh'}


@view_config(context=Users, renderer='users.mak', permission='loggedin')
def view_users(context, request):
    return {'users': list(context)}


@view_config(context=Forbidden)
def forbidden(request):
    if authenticated_userid(request):
        raise HTTPForbidden("You don't have enough permissions to access this page.")

    raise HTTPFound(location = request.resource_url(request.root['users'], 'login',
                                                    query={'ref':request.path}))


def already_logged_in(request):
    # If the user is logged in already, redirect
    if authenticated_userid(request):
        request.session.flash('You are already logged in.')
        return True
    
    return False
    
@view_config(context=Users, name='login', renderer='users/login.mak')
def login(context, request):
    if already_logged_in(request):
        raise HTTPFound(location = '/')

    if 'ref' in request.params:
        referer = request.params['ref']
    else:
        referer = '/'

    if referer == request.path:
        referer = '/'

    came_from = request.params.get('came_from', referer)

    username = ''

    # If the request is post, try to authenticate
    if 'form.submitted' in request.params:
        username = request.params['username']
        password = request.params['password']

        if username in context and context[username].check_password(password):
            headers = remember(request, username)
            raise HTTPFound(location = came_from,
                            headers  = headers)

        request.session.flash('Invalid username/password.')

    
    return {'came_from' : came_from,
            'username'  : username}

@view_config(context=Users, name='logout', permission='loggedin')
def logout(context, request):
    headers = forget(request)

    referrer = request.url

    if referrer == request.path_url:
        referrer = '/'

    request.session.flash('You are now logged out.')
    
    raise HTTPFound(location = referrer,
                    headers = headers)


@view_config(context=Users, name='register', renderer='users/register.mak')
def register(context, request):
    if already_logged_in(request):
        raise HTTPFound(location = '/')

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

        raise HTTPFound(location = request.resource_url(new_user, 'generate_token'))
    
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
        raise Forbidden()

    token = request.params['token']

    if context.confirm(token):
        request.session.flash('Your accound was verified, enjoy BooksExchange!')

        raise HTTPFound(location = '/',
                        headers  = remember(request, context.username))

    raise HTTPFound(location = request.resource_url(context,
                                                    'generate_token',
                                                    query = {'wrong':True}))


def json_to_book(b):
    id          = b['id']
    b           = b['volumeInfo']
    identifiers = [(i['type'], i['identifier'])
                   for i in b['industryIdentifiers']]
    book        = Book(b['title'], b['subtitle'], b['authors'], b['publisher'],
                       b['publishedDate'], identifiers, b['description'],
                       b['imageLinks'])
    book.googleId = id
    return book

@view_config(context=Books, name='search', renderer='books/search.mak')
def search(context, request):
    class BooksSchema(colander.SequenceSchema):
        book = BookSchema()

    class ResultSchema(colander.MappingSchema):
        items = BooksSchema()

    if request.method == 'POST':
        search_form = deform.Form(SearchSchema(), buttons=('Search',))
        
        query = request.POST.items()

        try:
            query = search_form.validate(query)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        try:
            rsp = context.catalogue.query(query['query'])
        except CatalogueException, e:
            raise HTTPInternalServerError("no response from catalogue: " +
                                          str(e))

        books = json.load(rsp)
        try:
            books = ResultSchema().deserialize(books)
        except colander.Invalid, e:
            raise HTTPInternalServerError(str(e.asdict()) + str(books))

        
        books = [json_to_book(vi) for vi in books['items']]

        return {'form': search_form.render(),
                'result': books}

    return {'result': []}


@view_config(context=Books, name='add', permission='loggedin')
def add_book(context, request):
    if len(request.subpath) == 1:
        id = request.subpath[0]
        
        try:
            book = context.catalogue.volume(id)
        except CatalogueException, e:
            raise HTTPInternalServerError("no responese from catalogue: " +
                                          str(e))

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
        raise HTTPFound(location = request.resource_url(context, 'list'))

    raise HTTPBadRequest("no book specified")



@view_config(context=Books, name='list', renderer='books/list.mak',
             permission='loggedin')
def list_book(context, request):
    user = request.user
    if user is None:
        raise HTTPInternalServerError("no user found")

    books = user.owned.itervalues()

    return {'books': books}
