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

from exceptions                     import RuntimeError

from persistent                     import Persistent
from persistent.list                import PersistentList
from persistent.mapping             import PersistentMapping

from pyramid.httpexceptions         import HTTPInternalServerError
from pyramid.security               import Allow, Everyone, Deny
from pyramid.traversal              import resource_path

from repoze.catalog.indexes.field   import CatalogFieldIndex
from repoze.catalog.indexes.text    import CatalogTextIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex


import bcrypt
import colander
import datetime
import datetime
import hashlib
import json
import urllib
import uuid

from booksexchange.schemas        import BookSchema
from booksexchange.utils          import (IndexFolder, GoogleBooksCatalogue,
                                          CatalogueException, substrings)

class App(PersistentMapping):
    __name__   = None
    __parent__ = None
    __acl__    = [(Allow, 'group:users', 'loggedin')]

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
        self.setchild('messages', Messages())
        self.setchild('cache', VerySimpleCache())


def groups_list(user, default):
    if not hasattr(user, 'groups'):
        return default

    return user.groups.keys()

def lowercase_sub_username(user, default):
    if hasattr(user, 'username'):
        return ' '.join(substrings(user.username))
    return default

class Users(IndexFolder):
    def __init__(self):
        super(Users, self).__init__(email    = CatalogFieldIndex('email'),
                                    groups   = CatalogFieldIndex(groups_list),
                                    username = CatalogTextIndex(lowercase_sub_username))

    def new_user(self, user):
        self[user.username] = user


class User(Persistent):
    def __init__(self, username, email, password):
        self._username  = username
        self.email      = email
        self.password   = password
        self.created    = datetime.datetime.utcnow()

        self.confirmed = False

        self.owned     = PersistentMapping()
        self.want      = PersistentMapping()

        self.groups    = PersistentMapping()

        self.conversations     = PersistentMapping()
        self.unread            = PersistentList()
        self.conversation_list = PersistentList()

        self.events    = PersistentList()

        self.location  = None
        self.about     = ''

    def __getitem__(self, key):
        if key in ['generate_token', 'confirm']:
            raise KeyError

        return self.owned[key]

    @property
    def username(self):
        return self._username

    def get_password(self):
        return self._password

    def set_password(self, plain_password):
        self._password = bcrypt.hashpw(plain_password, bcrypt.gensalt())

    password = property(get_password, set_password)

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
        check_class(book, Book, 'not a book. GTFO')
        self.owned[book.identifier] = book

    def add_want(self, book):
        check_class(book, Book, 'not a book. GTFO')
        self.want[book.identifier] = book

    def remove_book(self, book):
        check_class(book, Book, 'not a book. GTFO')
        ok = False
        if book.identifier in self.owned:
            del self.owned[book.identifier]
            ok = True
        if book.identifier in self.want:
            del self.want[book.identifier]
            ok = True
        return ok

    def add_group(self, group):
        check_class(group, Group, 'not a group')
        self.groups[group.identifier] = group

    def add_message(self, message, unread = True):
        check_class(message, Message, 'not a message')

        # Who's the other mofo?
        otheruser = message.recipient
        if otheruser is self:
            otheruser = message.sender

        # What conversation is this message part of?
        conversation = None
        if isinstance(message, Offer): # offers always start new conversatiosn
            message.reply_to = None
            if message.conversation is None:
                message.conversation = str(uuid.uuid1())
            conversation = message.conversation
        elif message.reply_to is not None:
            message.conversation = message.reply_to.conversation
            conversation = message.conversation
        if conversation is None:
            conversation = otheruser.username

        # If this is the first message, add it to the conversations
        # list.  Otherwise, append it to the relevant conversation.
        if conversation not in self.conversations:
            self.conversations[conversation] = PersistentList()
        self.conversations[conversation].append(message)

        # Add the current conversation to the unread list
        if conversation not in self.unread:
            self.unread.insert(0, conversation)

        # Re-add to the top of the conversation_list
        try:
            self.conversation_list.remove(conversation)
        except ValueError:
            pass
        self.conversation_list.insert(0, conversation)

    def message_read(self, message):
        self.unread.remove(message)

    def gravatar(self, size):
        gravatar_url = "http://www.gravatar.com/avatar/"

        gravatar =  gravatar_url + hashlib.md5(self.email.lower()).hexdigest() + "?"
        gravatar += urllib.urlencode({'s': str(size), 'd':'identicon'})

        return gravatar

    def add_event(self, event):
        check_class(event, Event, "that is not eventual enough")
        self.events.insert(0, event)

    def __dict__(self):
        return {"owned": self.owned,
                "want": self.want,
                "events": self.events,
                "gravatar": self.gravatar(64)}


def lowercase_title(book, default):
    return getattr(book, 'title', default).lower()

def lowercase_subtitle(book, default):
    return getattr(book, 'subtitle', default).lower()

class Books(IndexFolder):
    def __init__(self):
        super(Books, self).__init__(
            title    = CatalogTextIndex(lowercase_title),
            subtitle = CatalogTextIndex(lowercase_subtitle))

        self.catalogue = GoogleBooksCatalogue()

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
        book.owners = PersistentMapping()
        book.coveters = PersistentMapping()
        book.__name__ = id
        book.__parent__ = self
        return book

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

class Book(Persistent):
    def __init__(self, id, title, subtitle, authors, publisher, date,
                 identifiers, description, image_links):
        self.title       = title
        self.subtitle    = subtitle
        self.authors     = authors
        self.publisher   = publisher
        self.year        = date
        if self.year and isinstance(self.year, basestring):
            try:
                self.year = int(self.year[:4])
            except:
                pass
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
        check_class(user, User, "that is a cabbage, not a human")
        self.owners[user.username] = user

    def add_coveter(self, user):
        check_class(user, User, "that is a cabbage, not a human")
        self.coveters[user.username] = user

    def remove_user(self, user):
        check_class(user, User, "this is a cabbage, not a human")
        ok = False
        if user.username in self.coveters:
            del self.coveters[user.username]
            ok = True
        if user.username in self.owners:
            del self.owners[user.username]
            ok = True
        return ok

    def format_title(book):
        r = book.title
        if book.subtitle:
            r += "- " + book.subtitle
        if book.authors:
            r += "by "
            for author in book.authors:
                r += author + ", "
        return r

    def __dict__(self):
        r = {"identifier": self.identifier,
             "title": self.title,
             "subtitle": self.subtitle,
             "authors": self.authors,
             "publisher": self.publisher,
             "owners": self.owners.keys(),
             "coveters": self.coveters.keys(),
             "description": self.description,
             "thumbnail": "",
             "smallThumbnail": ""}
        if self.image_links is not None:
            r['thumbnail'] = self.image_links.get('thumbnail', '')
            r['smallThumbnail'] = self.image_links.get('smallThumbnail', '')
        return r

class Events(Persistent):
    def __init__(self):
        self.have     = PersistentList()
        self.want     = PersistentList()
        self.exchange = PersistentList()
        self.all      = PersistentList()

    def add_have(self, user, book):
        check_class(user, User, "not a User")
        check_class(book, Book, "not a Book")
        e = HaveEvent(user, book)
        self.have.insert(0, e)
        self.all.insert(0, e)
        user.add_event(e)

    def add_want(self, user, book):
        check_class(user, User, "not a User")
        check_class(book, Book, "not a Book")
        e = WantEvent(user, book)
        self.want.insert(0, e)
        self.all.insert(0, e)
        user.add_event(e)

    def add_exchange(self, giver, taker, apples, oranges, rating):
        check_class(giver, User, "not a User")
        check_class(taker, User, "not a User")
        check_class(apples, Book, "not a Book")
        check_class(oranges, Book, "not a Book")
        e = ExchangeEvent(giver, taker, apples, oranges, rating)
        self.exchange.insert(0, e)
        self.all.insert(0, e)
        giver.add_event(e)
        taker.add_event(e)

class Event(Persistent):
    def __init__(self):
        super(Event, self).__init__()

        self.date = datetime.datetime.utcnow()

    def __dict__(self):
        return {'date': self.date}


class HaveEvent(Event):
    def __init__(self, user, book):
        super(HaveEvent, self).__init__()

        self.owner = user
        self.book  = book

    def __dict__(self):
        r = super(HaveEvent, self).__dict__()
        r['event'] = 'have'
        r['book'] = self.book.identifier
        r['owner'] = self.owner.username
        return r

class WantEvent(Event):
    def __init__(self, user, book):
        super(WantEvent, self).__init__()

        self.coveter = user
        self.book    = book

    def __dict__(self):
        r = super(WantEvent, self).__dict__()
        r['event'] = 'want'
        r['book'] = self.book.identifier
        r['coveter'] = self.coveter.username
        return r


class ExchangeEvent(Event):
    def __init__(self, giver, taker, apples, oranges, rating):
        super(ExchangeEvent, self).__init__()

        self.giver   = giver
        self.taker   = taker
        self.apples  = apples
        self.oranges = oranges
        self.rating  = rating

    def __dict__(self):
        r = super(ExchangeEvent, self).__dict__()
        r['event'] = 'exchange'
        r['apples'] = [book.identifier for book in self.apples]
        r['oranges'] = [book.identifier for book in self.oranges]
        r['giver'] = self.giver.username
        r['taker'] = self.taker.username
        r['rating'] = self.rating
        return r



def lowercase_group_name(group, default):
    if hasattr(group, 'name'):
        return group.name.lower()
    return default

def lowercase_group_description(group, default):
    if hasattr(group, 'description'):
        return group.description.lower()
    return default


class Groups(IndexFolder):
    def __init__(self):
        super(Groups, self).__init__(
            name        = CatalogTextIndex(lowercase_group_name),
            description = CatalogTextIndex(lowercase_group_description))


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

        self.image       = None

    @property
    def identifier(self):
        return self._identifier

    def add_member(self, user):
        check_class(user, User, "that is a cabbage, not a human")

        self.members[user.username] = user

    def add_owner(self, user):
        check_class(user, User, "that is a cabbage, not a human")

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


class Messages(PersistentMapping):
    def __init__(self):
        super(Messages, self).__init__()

    def __getitem__(self, key):
        if key in ['new', 'list', 'offer']:
            raise KeyError
        return super(Messages, self).__getitem__(key)

    def new_message(self, message):
        self[message.identifier] = message
        message.__parent__ = self

class Message(Persistent):
    def __init__(self, sender, recipient, subject, body):
        super(Message, self).__init__()

        self.sender    = sender
        self.recipient = recipient
        self.subject   = subject
        self.body      = body

        self.reply_to  = None
        self.conversation = None

        self.date        = datetime.datetime.utcnow()
        self._identifier = str(uuid.uuid1())
        self.__name__    = self._identifier

    @property
    def identifier(self):
        return self._identifier

    def __dict__(self):
        return {"date": self.date,
                "sender": self.sender.username,
                "subject": self.subject,
                "recipient": self.recipient.username,
                "conversation": self.conversation,
                "body": self.body}

class Offer(Message):
    def __init__(self, sender, recipient, subject, body, apples, oranges):
        super(Offer, self).__init__(sender, recipient, subject, body)

        # the sender offers apples
        if not hasattr(apples, "__iter__"):
            apples = [apples]
        self.apples  = PersistentList(apples)

        # the receiver offer oranges
        if not hasattr(oranges, "__iter__"):
            oranges = [oranges]
        self.oranges = PersistentList(oranges)

    def __dict__(self):
        r = super(Offer, self).__dict__()
        r['apples']  = self.apples
        r['oranges'] = self.oranges

class Feedback(Message):
    def __init__(self, sender, recipient, rating, comment):
        super(Feedback, self).__init__(sender, recipient,
                                       "You've got feedback",
                                       "How about you return the favour?")

        self.rating  = rating
        self.comment = comment


class VerySimpleCache(Persistent):
    def __init__(self, max_keys = 10):
        super(VerySimpleCache, self).__init__()

        self.max_keys = max_keys

        self._values = PersistentMapping()
        self._keys   = PersistentList()

    def get(self, key, fun):
        if key not in self._values:
            self._values[key] = fun()
            self._keys.append(key)
            if len(self._keys) > self.max_keys:
                del self._values[self._keys[0]]
                del self._keys[0]
        return self._values[key]


def check_class(obj, klass, msg):
    if not isinstance(obj, klass):
        raise RuntimeError(msg)


def appmaker(zodb_root):
    from repoze.evolution import ZODBEvolutionManager
    from repoze.evolution import evolve_to_latest

    if not 'app_root' in zodb_root:
        app_root              = App()
        zodb_root['app_root'] = app_root

        app_root['users'].new_user(User('francesco', 'f@mazzo.li', 'francesco'))
        app_root['users']['francesco'].confirmed = True

        app_root['users'].new_user(User('scvalex', 'scvalex@gmail.com', 'scvalex'))
        app_root['users']['scvalex'].confirmed = True

        app_root['users'].new_user(User('ciccio', 'blah@blo.com', 'ciccio'))
        app_root['users']['ciccio'].confirmed = True

        app_root['users'].new_user(User('marco', 'marco@marco.com', 'marco'))
        app_root['users']['marco'].confirmed = True

        app_root['users'].new_user(User('max', 'max@max.com', 'max'))
        app_root['users']['max'].confirmed = True

        import transaction
        transaction.commit()

    # Evolve each sub-DB if necessary
    evolmgr_users = ZODBEvolutionManager(zodb_root['app_root']['users'],
                        evolve_packagename='booksexchange.dbevol.users',
                        sw_version=1, initial_db_version=0)
    evolve_to_latest(evolmgr_users)

    evolmgr_books = ZODBEvolutionManager(zodb_root['app_root']['books'],
                        evolve_packagename='booksexchange.dbevol.books',
                        sw_version=1, initial_db_version=0)
    evolve_to_latest(evolmgr_books)

    evolmgr_events = ZODBEvolutionManager(zodb_root['app_root']['events'],
                        evolve_packagename='booksexchange.dbevol.events',
                        sw_version=1, initial_db_version=0)
    evolve_to_latest(evolmgr_events)

    evolmgr_groups = ZODBEvolutionManager(zodb_root['app_root']['groups'],
                        evolve_packagename='booksexchange.dbevol.groups',
                        sw_version=1, initial_db_version=0)
    evolve_to_latest(evolmgr_groups)

    evolmgr_messages = ZODBEvolutionManager(zodb_root['app_root']['messages'],
                        evolve_packagename='booksexchange.dbevol.messages',
                        sw_version=1, initial_db_version=0)
    evolve_to_latest(evolmgr_messages)

    evolmgr_cache = ZODBEvolutionManager(zodb_root['app_root']['cache'],
                        evolve_packagename='booksexchange.dbevol.cache',
                        sw_version=1, initial_db_version=0)
    evolve_to_latest(evolmgr_cache)
    # Done evolving

    return zodb_root['app_root']
