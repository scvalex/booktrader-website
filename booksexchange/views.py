from pyramid.view           import view_config
from pyramid.url            import resource_url
from pyramid.exceptions     import Forbidden
from pyramid.security       import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from repoze.catalog.query   import Eq

import colander
import deform

from booksexchange.models   import App, Users, User


@view_config(context=App, renderer='home.mak')
def view_home(context, request):
    return {'blah': 'bloh'}

@view_config(context=Users, renderer='users.mak')
def view_users(context, request):
    return {'users': list(context)}


def already_logged_in(request):
    # If the user is logged in already, redirect
    if authenticated_userid(request):
        request.session.flash('You are already logged in.')
        
        return HTTPFound(location = resource_url(context, request))

@view_config(context=Forbidden)
def view_forbidden(request):
    if authenticated_userid(request):
        return HTTPForbidden()
    
    return HTTPFound(location = resource_url(request.root['users']['login']))

@view_config(context=Users, name='login', renderer='users/login.mak')
def view_login(context, request):

    already_logged_in(request)

    referrer  = request.url
    
    if referrer == request.path_url:
        referrer = '/'

    came_from = request.params.get('came_from', referrer)

    username = ''

    # If the request is post, try to authenticate
    if request.method == 'POST':
        username = request.params['username']
        password = request.params['password']

        if username in context and context[username].check_password(password):
            headers = remember(request, username)
            return HTTPFound(location = came_from,
                             headers  = headers)

        request.session.flash('Invalid username/password.')

    
    return dict(came_from   = came_from,
                username    = username)

@view_config(context=Users, name='logout')
def view_logout(context, request):
    headers = forget(request)
    return HTTPFound(location = resource_url(context, request),
                     headers = headers)


@view_config(context=Users, name='register', renderer='users/register.mak')
def view_register(context, request):

    already_logged_in(request)

    class UserValidator(colander.Length):
        def __init__(self, *args, **kwargs):
            super(UserValidator, self).__init__(*args, **kwargs)
        
        def __call__(self, node, value):
            super(UserValidator, self).__call__(node, value)
            
            if context.query(Eq('username', value))[0] != 0:
                raise colander.Invalid(node, '"' + value + '" is already taken.')

    class EmailValidator(colander.Email):
        def __init__(self, *args, **kwargs):
            super(EmailValidator, self).__init__(*args, **kwargs)

        def __call__(self, node, value):
            super(EmailValidator, self).__call__(node, value)
            
            if context.query(Eq('email', value))[0] != 0:
                raise colander.Invalid(node, 'The email you inserted is already present.')

    class RegisterSchema(colander.Schema):
        username = colander.SchemaNode(colander.String(),
                                       validator = UserValidator())
        password = colander.SchemaNode(colander.String(),
                                       validator = colander.Length(min=5, max=200),
                                       widget    = deform.widget.CheckedPasswordWidget(size=20))
        email    = colander.SchemaNode(colander.String(),
                                       validator = EmailValidator())
        

    schema = RegisterSchema()
    form   = deform.Form(schema, buttons=('Register',))

    if 'Register' in request.POST:
        controls = request.POST.items()

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
