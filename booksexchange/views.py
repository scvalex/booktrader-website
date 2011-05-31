from pyramid.view           import view_config
from pyramid.traversal      import resource_path
from pyramid.exceptions     import Forbidden
from pyramid.security       import remember, forget, authenticated_userid
from pyramid.httpexceptions import (HTTPFound, HTTPForbidden,
                                    HTTPInternalServerError, HTTPBadRequest,
                                    HTTPException, HTTPRedirection,
                                    HTTPNotFound)

from repoze.catalog.query   import Eq

from sets import Set

import colander
import deform
import json
import re

from booksexchange.models   import *
from booksexchange.schemas  import *
from booksexchange.utils    import send_email, CatalogueException


@view_config(context=HTTPRedirection)
def httpexception(context, request):
    return context


@view_config(context=App, renderer='home.mak')
def home(context, request):
    return {'events': context['events']}


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

    class LoginSchema(colander.Schema):
        username  = colander.SchemaNode(colander.String())
        password  = colander.SchemaNode(colander.String(),
                                        widget  = deform.widget.PasswordWidget())
        came_from = colander.SchemaNode(colander.String(),
                                        widget  = deform.widget.HiddenWidget(),
                                        default = referer)

    def validate_login(form, value):
        exc = colander.Invalid(form, '')
        exc['username'] = 'Invalid username/password.'
        if value['username'] not in context:
            raise exc

        if not context[value['username']].check_password(value['password']):
            raise exc

    form = deform.Form(LoginSchema(validator = validate_login),
                       buttons = ('Login',))

    if 'Login' in request.params:
        controls = request.params.items()

        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        request.session.flash('You are now logged in.')

        raise HTTPFound(location = data['came_from'],
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
             renderer='users/registration_token.mak')
def registration_token(context, request):
    if context.confirmed:
        raise HTTPNotFound()
    
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
            'want':  context.want.values()}


@view_config(context=Books, name='search', renderer='books/search.mak')
def search(context, request):
    class BooksSchema(colander.SequenceSchema):
        book = BookSchema()

    class ResultSchema(colander.MappingSchema):
        items = BooksSchema(missing=[])
        totalItems = colander.SchemaNode(colander.Integer())

    if 'Search' in request.params:
        search_form = deform.Form(SearchSchema(), buttons=('Search',))

        query = request.params.items()

        try:
            query = search_form.validate(query)
        except deform.ValidationFailure, e:
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

        return {'form': search_form.render(),
                'total_items': total_items, 'result': books,
                'page_indices': page_indices, 'page_index': start_index / 10,
                'make_url': make_url,
                'next_url': next_url, 'prev_url': prev_url}

    return {'result': []}


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

@view_config(context=Groups, name='create', permission='loggedin',
             renderer='groups/create_group.mak')
def create_group(context, request):
    schema = GroupSchema()
    form   = deform.Form(schema, buttons=('Create Group',))

    if 'Create Group' in request.params:
        controls = request.params.items()

        try:
            group_data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        new_group = Group(group_data['name'],
                          group_data['description'],
                          group_data['type'])
        context[new_group.identifier] = new_group

        new_group.add_member(request.user)
        new_group.add_owner(request.user)
        request.user.add_group(new_group)
        request.root['users'].update(request.user)
        request.root['groups'].update(new_group)

        request.session.flash('Your group has been created.')

        raise HTTPFound(location = request.resource_url(new_group))

    return {'form': form.render()}

@view_config(context=Group, renderer='groups/view.mak', permission='view_group')
def view_group(context, request):
    return {}


def join_group_success(context, request):
    request.user.add_group(context)
    context.add_member(request.user)
    request.root['users'].update(request.user)
    request.root['groups'].update(context)

    request.session.flash('You are now a member of ' + context.name + '!')

    raise HTTPFound(location = request.resource_url(context))


@view_config(context=Group, name='confirm_join', permission='join_group')
def confirm_join_group(context, request):
    if 'token' in request.params:
        if context.confirm_user(request.user, request.params['token']):
            join_group_success(context, request)
        else:
            request.session.flash('The token provided is wrong, please try again.')
            raise HTTPFound(location = request.resource_url(context, 'join'))

    raise HTTPBadRequest('No token provided.')

@view_config(context=Group, name='join', permission='join_group',
             renderer='groups/join.mak')
def join_group(context, request):
    if context.type == 'public':
        join_group_success(context, request)

    elif context.type == 'private':

        def validate_email(node, value):
            colander.Length(max=255)(node, value)

            for domain in context.domains:
                if value.endswith('@' + domain):
                    return

            error_email = "The email you inserted doesn't belong " + \
                          "to one of the required domains."
            raise colander.Invalid(node, error_email)

        class GroupEmail(colander.MappingSchema):
            email = colander.SchemaNode(colander.String(), validator=validate_email)

        form = deform.Form(schema=GroupEmail(), buttons=('Join',))

        if 'Join' in request.params:
            controls = request.params.items()

            try:
                data = form.validate(controls)
            except deform.ValidationFailure, e:
                return {'form': e.render()}

            token = context.generate_token(request.user)

            confirm_url = request.resource_url(context, 'confirm_join',
                                               query = {'token': token})

            email_body = "Dear " + request.user.username + ",\n\n" + \
                         "To join group " + context.name +"," \
                         "please click visit this link: " + confirm_url + ".\n\n" + \
                         "The BooksExchange team."


            send_email(email_body, 'BooksExchange group.',
                       [data['email']], request.registry.settings)

            return {'form':None}

        return {'form': form.render()}


@view_config(context=Group, name='admin', permission='admin_group',
             renderer='groups/admin.mak')
def admin_group(context, request):

    class DomainsSchema(colander.SequenceSchema):
        domain = colander.SchemaNode(utf8_string(),
                                     validator = colander.Length(min=3, max=255),
                                     title     = 'Domain')
    class GroupAdminSchema(GroupSchema):
        domains = DomainsSchema()


    if context.type == 'public':
        schema = GroupSchema()
    else:
        schema = GroupAdminSchema()
        schema['domains'].default = context.domains


    form = deform.Form(schema, buttons=('Submit',))

    choices = [(context.type, context.type.capitalize())]
    for t in Group.types:
        if t != context.type:
            choices.append((t, t.capitalize()))

    form.schema['type'].widget.values  = choices
    form.schema['name'].default        = context.name
    form.schema['description'].default = context.description

    if 'Submit' in request.params:
        controls = request.params.items()

        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form': e.render()}

        context.name        = data['name']
        context.description = data['description']
        context.type        = data['type']
        if 'domains' in data:
            context.domains = data['domains']

        request.root['groups'].update(context)

        raise HTTPFound(location = request.url)


    return {'form': form.render()}


@view_config(context=Messages, name='list', permission='loggedin',
             renderer='messages/list.mak')
def list_messages(context, request):
    return {'conversations': request.user.conversations,
            'conversation_list': request.user.conversation_list,
            'unread': request.user.unread,
            'msg': None}


def make_message_schema(users, current_user, other_user = None,
                        typ = "message"):
    class MessageSchema(colander.MappingSchema):
        def validate_user_exists(node, username):
            if username == current_user.username or username not in users:
                raise colander.Invalid(node, 'User "' + username +
                                       '" does not exist.')

        recipient = colander.SchemaNode(utf8_string(),
                                        validator = validate_user_exists)
        subject   = colander.SchemaNode(utf8_string())
        body      = colander.SchemaNode(utf8_string(),
                                        widget = deform.widget.TextAreaWidget(),
                                        validator = colander.Length(min = 17))

    class OfferSchema(MessageSchema):
        def validate_book_exists(node, user, book):
            if user is None or book not in user.owned:
                raise colander.Invalid(node, 'User "' + user.username +
                                       '" does not have book "' + book + '"')

        def validate_my_book(node, book):
            return validate_book_exists(node, current_user, book)

        def validate_other_book(node, book):
            return validate_book_exists(node, other_user, book)

        def pretty_title(book):
            if not book.authors:
                return book.title
            return book.title + " by " + book.authors[0]

        apples = colander.SchemaNode(
            utf8_string(),
            validator = validate_my_book,
            widget = deform.widget.SelectWidget(
                values = [(book.identifier, pretty_title(book))
                          for book in current_user.owned.values()]))

        oranges = colander.SchemaNode(
            utf8_string(),
            validator = validate_other_book,
            widget = deform.widget.SelectWidget(
                values = [(book.identifier, pretty_title(book))
                          for book in other_user.owned.values()]))

    if typ == "message":
        return MessageSchema()
    elif typ == "offer":
        return OfferSchema()
    else:
        raise RuntimeError("unknown message schema: " + typ)

@view_config(context=Messages, name='new', permission='loggedin',
             renderer='messages/new.mak')
def send_message(context, request):
    form = deform.Form(make_message_schema(request.root['users'],
                                           request.user),
                       buttons=('Send',))

    if request.method == 'POST':
        common_send_message(context, request, form, lambda msg: msg)

    return {'form': form.render(), 'typ': "message"}

@view_config(context=Messages, name='offer', permission='loggedin',
             renderer='messages/new.mak')
def send_offer(context, request):
    form = deform.Form(make_message_schema(request.root['users'],
                                           request.user, request.user,
                                           'offer'),
                       buttons=('Send',))

    if request.method == 'POST':
        common_send_message(context, request, form, lambda msg: msg)

    return {'form': form.render(), 'typ': "offer"}

@view_config(context=Message, name='reply', renderer='messages/new.mak')
def reply_to_message(context, request):
    if request.user is not context.sender and request.user is not context.recipient:
        raise Forbidden()

    form = deform.Form(make_message_schema(request.root['users'],
                                           request.user),
                       buttons=('Send',))
    recipient = context.sender.username
    if recipient == request.user.username:
        recipient = context.recipient.username
    form.schema['recipient'].default = recipient
    form.schema['subject'].default = "Re: " + context.subject

    if request.method == 'POST':
        def extra_fun(message):
            message.reply_to = request.user.conversations[context.identifier][-1] # reply to the *last* message in the conversation context
        common_send_message(context, request, form, extra_fun)

    return {'form': form.render()}

def common_send_message(context, request, form, extra_fun):
    controls = request.POST.items()

    try:
        data = form.validate(controls)
    except deform.ValidationFailure, e:
        controls = dict(controls)
        form.schema['recipient'].default = controls.get('recipient', '')
        form.schema['subject'].default = controls.get('subject', '')
        form.schema['body'].default = controls.get('body', '')
        return {'form': e.render()}

    recipient = request.root['users'][data['recipient']]

    m = Message(request.user, recipient, data['subject'], data['body'])
    extra_fun(m)
    request.root['messages'].new_message(m)
    recipient.add_message(m)
    request.user.add_message(m, unread = False)

    request.session.flash('Message sent!')

    raise HTTPFound(location = request.resource_url(request.root['messages'], 'list'))


@view_config(context=Message, renderer='messages/list.mak')
def show_message(context, request):
    if request.user is not context.sender and request.user is not context.recipient:
        raise Forbidden()

    first_message = context
    while first_message.reply_to is not None:
        first_message = first_message.reply_to

    if first_message in request.user.unread:
        request.user.unread.remove(first_message)

    return {'conversations': request.user.conversations,
            'conversation_list': request.user.conversation_list,
            'unread': request.user.unread,
            'msg': first_message}
