from booksexchange.views.common import *

@view_config(context=Users, renderer='users.mak', permission='loggedin')
def view_users(context, request):
    return {'users': list(context)}

def already_logged_in(request):
    """
    Function to use in views in which you need to redirect the user is
    already logged in.
    """
    if authenticated_userid(request):
        request.session.flash('You are already logged in.')
        return True

    return False

@view_config(context=Users, name='login', renderer='users/login.mak')
def login(context, request):
    if already_logged_in(request):
        raise HTTPFound(location = '/')

    if 'came_from' in request.params:
        referer = request.params['came_from']
    elif request.referer:
        referer = request.referer
    else:
        referer = '/'

    if referer == request.path:
        referer = '/'

    class LoginSchema(colander.Schema):
        username  = colander.SchemaNode(colander.String())
        password  = colander.SchemaNode(colander.String(),
                                        widget  = deform.widget.PasswordWidget())
        came_from = colander.SchemaNode(colander.String(),
                                        widget  = deform.widget.HiddenWidget(),
                                        missing = '/',
                                        default = referer)

    def validate_login(form, value):
        exc = colander.Invalid(form, '')
        exc['username'] = 'Invalid username/password.'
        if value['username'] not in context:
            raise exc

        if not context[value['username']].check_password(value['password']):
            raise exc

    form = deform.Form(LoginSchema(validator = validate_login), buttons = ('Login',))

    if 'Login' in request.params:
        controls = request.params.items()

        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        request.session.flash('You are now logged in.')

        raise HTTPFound(location = referer,
                        headers  = remember(request, data['username']))

    return {'form': form.render()}

@view_config(context=Users, name='logout')
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

        if value in context:
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
             renderer='users/registration_token.mak')
def registration_token(context, request):
    if context.confirmed:
        raise HTTPBadRequest("user already confirmed")

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
def confirm_registration(context, request):
    if not 'token' in request.params or context.confirmed:
        raise Forbidden()

    token = request.params['token']

    if context.confirm(token):
        request.session.flash('Your account was verified, enjoy BooksExchange!')

        raise HTTPFound(location = '/',
                        headers  = remember(request, context.username))

    raise HTTPFound(location = request.resource_url(context,
                                                    'generate_token',
                                                    query = {'wrong':True}))


@view_config(context=User, renderer='users/home.mak')
def user_home(context, request):
    return {'owned': context.owned.values(),
            'want':  context.want.values(),
            'events': context.events}
