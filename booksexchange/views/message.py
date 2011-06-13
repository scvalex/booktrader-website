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
        subject   = colander.SchemaNode(utf8_string())
        body      = colander.SchemaNode(
            utf8_string(),
            widget = deform.widget.TextAreaWidget())

    def validate_book_exists(node, user, book):
        if user is None or book not in user.owned:
            raise colander.Invalid(node, 'User "' + user.username +
                                   '" does not have book "' + book + '"')

    def validate_my_book(node, book):
        return validate_book_exists(node, current_user, book)

    def validate_other_book(node, book):
        return validate_book_exists(node, other_user, book)

    class OfferSchema(MessageSchema):
        apples = colander.SchemaNode(
            utf8_string(),
            validator = validate_my_book,
            widget = deform.widget.SelectWidget(values = my_books))

        oranges = colander.SchemaNode(
            utf8_string(),
            validator = validate_other_book,
            widget = deform.widget.SelectWidget(values = other_books))

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
    if not isinstance(context, Offer) or request.user is not context.recipient:
        raise Forbidden()

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

    set_recipient(form, context.sender)

    if request.method == 'POST':
        def extra_fun(message):
            message.reply_to = context # reply to the *last* message in the conversation context
            request.root['events'].add_exchange(context.sender, context.recipient, context.apples, context.oranges, message.rating)
        common_send_message(context, request, form, extra_fun,
                            context.sender, 'feedback')

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
                  id_to_book(data['apples']), id_to_book(data['oranges']))
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

def get_other(message, request):
    other = message.sender
    if other is request.user:
        other = message.recipient
    return other
