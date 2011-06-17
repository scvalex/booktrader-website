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


@view_config(context=Messages, name='list', permission='loggedin',
             renderer='messages/list.mak')
def list_messages(context, request):
    return {'conversations': request.user.conversations,
            'conversation_list': request.user.conversation_list,
            'unread': request.user.unread,
            'msg_root': None}


def make_message_schema(users, current_user, other_user = None,
                        typ = "message"):
    def pretty_title(book):
        if not book.authors:
            return book.title
        return book.title + " by " + book.authors[0]

    my_books = [(book.identifier, pretty_title(book))
                for book in current_user.owned.values()]
    if other_user is not None:
        other_books = [(book.identifier, pretty_title(book))
                       for book in other_user.owned.values()]
    else:
        other_books = []

    class MessageSchema(colander.MappingSchema):
        def validate_user_exists(node, username):
            if username == current_user.username or username not in users:
                raise colander.Invalid(node, 'User "' + username +
                                       '" does not exist.')

        recipient = colander.SchemaNode(
            utf8_string(),
            validator = validate_user_exists,
            widget = deform.widget.TextInputWidget())
        subject   = colander.SchemaNode(utf8_string(),
                                        missing = "")
        body      = colander.SchemaNode(
            utf8_string(),
            widget = deform.widget.TextAreaWidget(),
            missing = "")

    def validate_book_exists(node, user, book):
        if user is None or book not in user.owned:
            raise colander.Invalid(node, 'User "' + user.username +
                                   '" does not have book "' + book + '"')

    def validate_my_book(node, book):
        return validate_book_exists(node, current_user, book)

    def validate_other_book(node, book):
        return validate_book_exists(node, other_user, book)

    class ApplesSchema(colander.SequenceSchema):
        apple = colander.SchemaNode(
            utf8_string(),
            validator = validate_my_book,
            widget = deform.widget.SelectWidget(values = my_books))

    class OrangesSchema(colander.SequenceSchema):
        orange = colander.SchemaNode(
            utf8_string(),
            validator = validate_other_book,
            widget = deform.widget.SelectWidget(values = other_books))

    class OfferSchema(MessageSchema):
        apples = ApplesSchema()
        oranges = OrangesSchema()

    if typ == "message":
        return MessageSchema()
    elif typ == "offer":
        sch = OfferSchema()
        sch['oranges'].typ.accept_scalar = True
        sch['apples'].typ.accept_scalar = True
        return sch
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

def set_recipient(form, user):
    form.schema['recipient'].default = user.username
    form.schema['recipient'].widget.template = form.schema['recipient'].widget.readonly_template

@view_config(context=Book, name='offer', permission='loggedin',
             renderer='messages/new.mak')
def send_offer(context, request):
    try:
        other = request.root['users'][request.path.split('/')[2]]
    except Exception:
        raise HTTPBadRequest('request not specific enough: owner missing')

    form = deform.Form(make_message_schema(request.root['users'],
                                           request.user, other, 'offer'),
                       buttons=('Send',))

    set_recipient(form, other)
    form.schema['oranges'].default = context.identifier

    if request.method == 'POST':
        common_send_message(context, request, form, lambda msg: msg,
                            other, 'offer')

    return {'form': form.render(), 'typ': "offer"}

@view_config(context=Message, name='offer', renderer='messages/new.mak',
             permission='loggedin')
def reply_to_message_offer(context, request):
    if request.user is not context.sender and request.user is not context.recipient:
        raise Forbidden()

    recipient = get_other(context, request)

    form = deform.Form(make_message_schema(request.root['users'],
                                           request.user, recipient, 'offer'),
                       buttons=('Send',))
    set_recipient(form, recipient)

    form.schema['subject'].default = context.subject

    if request.method == 'POST':
        def extra_fun(message):
            message.reply_to = request.user.conversations[recipient.username][-1] # reply to the *last* message in the conversation context
        common_send_message(context, request, form, extra_fun,
                            recipient, 'offer')

    return {'form': form.render(), 'typ': "offer"}

@view_config(context=Message, name='reply', renderer='messages/new.mak',
             permission='loggedin')
def reply_to_message(context, request):
    if request.user is not context.sender and request.user is not context.recipient:
        raise Forbidden()

    form = deform.Form(make_message_schema(request.root['users'],
                                           request.user),
                       buttons=('Send',))

    recipient = get_other(context, request)

    set_recipient(form, recipient)

    form.schema['subject'].default = context.subject

    if request.method == 'POST':
        def extra_fun(message):
            if context.conversation is not None:
                message.reply_to = request.user.conversations[context.conversation][-1]
            else:
                message.reply_to = request.user.conversations[recipient.username][-1] # reply to the *last* message in the conversation context
        common_send_message(context, request, form, extra_fun, recipient)

    return {'form': form.render(), 'typ': 'message'}

@view_config(context=Message, name='complete', renderer='messages/new.mak',
             permission='loggedin')
def complete_exchange(context, request):
    if not isinstance(context, Offer) or (request.user is not context.recipient and request.user is not context.sender):
        raise Forbidden()

    if request.user in context.left_feedback:
        raise HTTPBadRequest("already left feedback")

    if len(context.accepted) != 2:
        raise HTTPBadRequest("both parties have not accepted yet")

    class FeedbackSchema(colander.MappingSchema):
        def validate_user_exists(node, username):
            if username == request.user.username or username not in request.root['users']:
                raise colander.Invalid(node, 'User "' + username +
                                       '" does not exist.')

        recipient = colander.SchemaNode(
            utf8_string(),
            validator = validate_user_exists,
            widget = deform.widget.TextInputWidget())
        rating = colander.SchemaNode(
            colander.Boolean(),
            widget = deform.widget.SelectWidget(values =
                                                ((1, 'Yes'), (0, 'No'))),
            title = "In hindsight, would you make this trade again?")
        comment      = colander.SchemaNode(
            utf8_string(),
            widget = deform.widget.TextInputWidget())

    form = deform.Form(FeedbackSchema(), buttons=('Submit',))

    recipient = get_other(context, request)
    set_recipient(form, recipient)

    if request.method == 'POST':
        def extra_fun(message):
            message.reply_to = context # reply to the *last* message in the conversation context
            request.root['events'].add_exchange(context.sender, context.recipient, context.apples, context.oranges, message.rating)
            message.offer = context
            context.left_feedback.append(request.user)
        common_send_message(context, request, form, extra_fun,
                            recipient, 'feedback')

    return {'form': form.render(), 'typ': 'feedback'}

def common_send_message(context, request, form, extra_fun, other = None,
                        typ = 'message'):
    controls = request.POST.items()

    if other is not None:
        controls.append(('recipient', other.username))

    try:
        data = form.validate(controls)
    except deform.ValidationFailure, e:
        controls = dict(controls)
        form.schema['recipient'].default = controls.get('recipient', '')
        if typ in ['message', 'offer']:
            form.schema['subject'].default = controls.get('subject', '')
            form.schema['body'].default = controls.get('body', '')
        if typ == 'offer':
            form.schema['apples'].default = controls.get('apples', '')
            form.schema['oranges'].default = controls.get('oranges', '')
        if typ == 'feedback':
            form.schema['rating'].default = controls.get('rating', 1)
            form.schema['comment'].default = controls.get('comment', '')

        return {'form': e.render()}

    recipient = request.root['users'][data['recipient']]

    def id_to_book(id):
        return request.root['books'][id]

    if typ == 'message':
        m = Message(request.user, recipient, data['subject'], data['body'])
    elif typ == 'offer':
        m = Offer(request.user, recipient, data['subject'], data['body'],
                  [id_to_book(id) for id in list(set(data['apples']))],
                  [id_to_book(id) for id in list(set(data['oranges']))])
    elif typ == 'feedback':
        m = Feedback(request.user, recipient, data['rating'], data['comment'])
    else:
        raise HTTPInternalServerError('unknown message type: ' + typ)
    extra_fun(m)
    request.root['messages'].new_message(m)
    recipient.add_message(m)
    request.user.add_message(m, unread = False)

    request.session.flash('Message sent!')

    raise HTTPFound(location = request.resource_url(m))


@view_config(context=Message, renderer='messages/list.mak')
def show_message(context, request):
    if request.user is not context.sender and request.user is not context.recipient:
        raise Forbidden()

    conversation = context.conversation
    if conversation is None:
        conversation = get_other(context, request).username

    try:
        request.user.unread.remove(conversation)
    except ValueError:
        pass

    return {'conversations': request.user.conversations,
            'conversation_list': request.user.conversation_list,
            'unread': request.user.unread,
            'msg_root': request.user.conversations[conversation]}

@view_config(context=Message, name='edit_offer', renderer='messages/new.mak',
             permission='loggedin')
def edit_offer(context, request):
    if (request.user is not context.sender and request.user is not context.recipient) or not isinstance(context, Offer):
        raise Forbidden()

    if context.accepted:
        raise HTTPBadRequest("cannot edit a closing offer")

    recipient = get_other(context, request)

    form = deform.Form(make_message_schema(request.root['users'],
                                           context.recipient, context.sender,
                                           'offer'),
                       buttons=('Send',))

    set_recipient(form, recipient)
    form.schema['subject'].default = context.subject
    form.schema['body'].default = context.body
    form.schema['apples'].default = [book.identifier for book in context.apples]
    form.schema['oranges'].default = [book.identifier for book in context.oranges]

    if request.method == 'POST':
        controls = request.POST.items()

        controls.append(('recipient', recipient.username))

        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            controls = dict(controls)
            form.schema['recipient'].default = controls.get('recipient', '')
            form.schema['subject'].default = controls.get('subject', '')
            form.schema['body'].default = controls.get('body', '')
            form.schema['apples'].default = controls.get('apples', [])
            form.schema['oranges'].default = controls.get('oranges', [])

            return {'form': e.render(), 'typ': 'offer'}

        def id_to_book(id):
            return request.root['books'][id]

        context.subject = data['subject']
        context.subject = data['body']
        context.apples = [id_to_book(id) for id in list(set(data['apples']))]
        context.oranges = [id_to_book(id) for id in list(set(data['oranges']))]
        request.user.message_unread(context)
        request.session.flash('Offer edited')

        raise HTTPFound(location = request.resource_url(context))

    return {'form': form.render(), 'typ': "offer"}

@view_config(context=Message, name='accept_offer',
             renderer='messages/list.mak',
             permission='loggedin')
def accept_offer(context, request):
    if (request.user is not context.sender and request.user is not context.recipient) or not isinstance(context, Offer):
        raise Forbidden()

    if request.user in context.accepted:
        raise HTTPBadRequest("already accepted")

    context.accepted.append(request.user)
    request.session.flash('Offer accpeted!')

    raise HTTPFound(location = request.resource_url(context))

def get_other(message, request):
    other = message.sender
    if other is request.user:
        other = message.recipient
    return other
