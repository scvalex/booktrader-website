import datetime

from exceptions                   import RuntimeError

from pyramid.security             import Allow, Everyone, Deny
from pyramid.traversal            import resource_path
from pyramid.httpexceptions       import HTTPInternalServerError

from persistent                   import Persistent
from persistent.list              import PersistentList
from persistent.mapping           import PersistentMapping

from repoze.catalog.indexes.field import CatalogFieldIndex

from booksexchange.utils          import (IndexFolder, GoogleBooksCatalogue,
                                          CatalogueException)
from booksexchange.schemas        import BookSchema

import bcrypt
import uuid
import json
import colander
import datetime

class App(PersistentMapping):
    __name__   = None
    __parent__ = None
    __acl__    = [ (Allow, 'group:users', 'loggedin') ]

    def setchild(self, name, obj):
        self[name]     = obj
        obj.__name__   = name
        obj.__parent__ = self

    def __init__(self):
        super(App, self).__init__()
        self.setchild('users', Users())
        self.setchild('books', Books())
        self.setchild('events', Events())
        self.setchild('groups', Groups())


class Users(IndexFolder):
    def __init__(self):
        super(Users, self).__init__(email    = CatalogFieldIndex('email'),
                                    username = CatalogFieldIndex('username'))

    def new_user(self, user):
        self[user.username] = user


class User(Persistent):
    def __init__(self, username, email, password):
        self._username  = username
        self.email      = email
        self._password  = bcrypt.hashpw(password, bcrypt.gensalt())
        self.created    = datetime.datetime.utcnow()

        self.confirmed = False

        self.owned     = PersistentMapping()
        self.want      = PersistentMapping()

        self.groups    = PersistentMapping()

        self.mailbox   = PersistentMapping()
        self.unread    = PersistentList()

    @property
    def username(self):
        return self._username

    def check_password(self, plain_password):
        return bcrypt.hashpw(plain_password, self._password) == self._password

    def generate_token(self):
        token = str(uuid.uuid4())
        self._token = token
        return token

    def confirm(self, token):
        if not hasattr(self, '_token'):
            return False

        if self._token == token:
            self.confirmed = True
            return True

        return False

    def add_owned(self, book):
        if not isinstance(book, Book):
            raise RuntimeError('not a book. GTFO')
        self.owned[book.identifier] = book

    def add_want(self, book):
        if not isinstance(book, Book):
            raise RuntimeError('not a book. GTFO')
        self.want[book.identifier] = book

    def add_group(self, group):
        if not isinstance(group, Group):
            raise RuntimeError('not a group')
        self.groups[group.identifier] = group

    def add_message(self, message):
        if not isinstance(message, Message):
            raise RuntimeError('not a message')
        self.mailbox[message.identifier] = message
        self.unread.insert(0, message)


class Books(IndexFolder):
    def __init__(self):
        super(Books, self).__init__()

        self.catalogue = GoogleBooksCatalogue()

    def __getitem__(self, key):
        if key in ['search', 'add']:
            raise KeyError

        try:
            return super(Books, self).__getitem__(key)
        except KeyError, e:
            try:
                b = BookSchema().deserialize(json.load(self.catalogue.volume(key)))
                return self.json_to_book(b)
            except CatalogueException, e:
                raise HTTPInternalServerError('no response from catalogue: ' + str(e))
            except colander.Invalid, e:
                raise HTTPInternalServerError(str(e.asdict()) + str(key))

    def new_book(self, book):
        self[book.identifier] = book

    def json_to_book(self, b):
        id          = b['id']

        if id in self:
            return self[id]

        b           = b['volumeInfo']
        identifiers = [(i['type'], i['identifier'])
                       for i in b['industryIdentifiers']]
        book        = Book(id, b['title'], b['subtitle'], b['authors'],
                           b['publisher'], b['publishedDate'],
                           identifiers, b['description'],
                           b['imageLinks'])
        return book


class Book(Persistent):
    def __init__(self, id, title, subtitle, authors, publisher, date,
                 identifiers, description, image_links):
        self.title       = title
        self.subtitle    = subtitle
        self.authors     = authors
        self.publisher   = publisher
        self.year        = date
        if self.year and isinstance(self.year, basestring):
            self.year = int(self.year[:4])
        self.identifiers = identifiers
        self.description = description
        self.image_links = image_links

        self._identifier = id

        self.owners      = PersistentMapping()
        self.coveters    = PersistentMapping()

    @property
    def identifier(self):
        return self._identifier

    def add_owner(self, user):
        if not isinstance(user, User):
            raise RuntimeError("that is a cabbage, not a human")
        self.owners[user.username] = user

    def add_coveter(self, user):
        if not isinstance(user, User):
            raise RuntimeError("that is a cabbage, not a human")
        self.coveters[user.username] = user


class Events(object):
    def __init__(self):
        self.have     = PersistentList()
        self.want     = PersistentList()
        self.exchange = PersistentList()
        self.all      = PersistentList()

    def add_have(self, user, book):
        e = HaveEvent(user, book)
        self.have.insert(0, e)
        self.all.insert(0, e)

    def add_want(self, user, book):
        e = WantEvent(user, book)
        self.want.insert(0, e)
        self.all.insert(0, e)

    def add_exchange(self, giver, taker, book):
        e = ExchangeEvent(giver, taker, book)
        self.exchange.insert(0, e)
        self.all.insert(0, e)

class Event(object):
    def __init__(self):
        super(Event, self).__init__()

        self.date = datetime.datetime.utcnow()


class HaveEvent(Event):
    def __init__(self, user, book):
        super(HaveEvent, self).__init__()

        self.owner = user
        self.book  = book

class WantEvent(Event):
    def __init__(self, user, book):
        super(WantEvent, self).__init__()

        self.coveter = user
        self.book    = book

class ExchangeEvent(Event):
    def __init__(self, giver, taker, book):
        super(ExchangeEvent, self).__init__()

        self.giver = giver
        self.taker = taker
        self.book  = book



class Groups(IndexFolder):
    def __init__(self):
        super(Groups, self).__init__(name = CatalogFieldIndex('name'))


class Group(Persistent):
    types = ['public', 'private']

    def __init__(self, name, description, type):
        self.name        = name
        self.description = description
        if type not in self.types:
            raise RuntimeError(type + ' is not a valid group type.')
        self.type        = type

        self.created     = datetime.datetime.utcnow()

        self._identifier = str(uuid.uuid1())

        self.members     = PersistentMapping()
        self.owners      = PersistentMapping()

        self.domains     = PersistentList()
        self.tokens      = PersistentMapping()

    @property
    def identifier(self):
        return self._identifier

    def add_member(self, user):
        if not isinstance(user, User):
            raise RuntimeError("that is a cabbage, not a human")

        self.members[user.username] = user

    def add_owner(self, user):
        if not isinstance(user, User):
            raise RuntimeError("that is a cabbage, not a human")

        self.owners[user.username] = user

    def remove_user(self, user):
        del self.member[user.username]

        if user.username in self.owners:
            del self.owners[user.username]

    @property
    def members_group(self):
        return 'group:' + self.identifier + ':member'

    @property
    def owners_group(self):
        return 'group:' + self.identifier + ':owner'

    @property
    def __acl__(self):
        return [(Allow, Everyone, 'view_group'),
                (Deny,  self.members_group, 'join_group'),
                (Allow, 'group:users', 'join_group'),
                (Allow, self.owners_group, 'admin_group')]

    def generate_token(self, user):
        token = str(uuid.uuid4())
        self.tokens[user.username] = token
        return token

    def confirm_user(self, user, token):
        if user.username in self.tokens and \
                self.tokens[user.username] == token:
            del self.tokens[user.username]
            return True
        return False


class Message(object):
    def __init__(self, sender, body):
        super(Message, self).__init__()

        self.sender = sender
        self.body = body


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root              = App()
        zodb_root['app_root'] = app_root

        app_root['users'].new_user(User('francesco', 'f@mazzo.li', 'francesco'))
        app_root['users']['francesco'].confirmed = True

        app_root['users'].new_user(User('scvalex', 'scvalex@gmail.com', 'scvalex'))
        app_root['users']['scvalex'].confirmed = True

        import transaction
        transaction.commit()
    return zodb_root['app_root']
