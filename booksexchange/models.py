import datetime

from exceptions                   import RuntimeError

from pyramid.security             import Allow, Everyone
from pyramid.traversal            import resource_path
from pyramid.httpexceptions       import HTTPInternalServerError

from persistent                   import Persistent
from persistent.mapping           import PersistentMapping

from repoze.catalog.indexes.field import CatalogFieldIndex

from booksexchange.utils          import (IndexFolder, GoogleBooksCatalogue,
                                          CatalogueException)
from booksexchange.schemas        import BookSchema

import bcrypt
import uuid
import json
import colander

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


class Users(IndexFolder):
    def __init__(self):
        super(Users, self).__init__(email    = CatalogFieldIndex('email'),
                                    username = CatalogFieldIndex('username'))

    def new_user(self, user):
        self[user.username] = user


class User(Persistent):
    def __init__(self, username, email, password):
        self.username   = username
        self.email      = email
        self._password  = bcrypt.hashpw(password, bcrypt.gensalt())
        self.created    = datetime.datetime.utcnow()

        self.confirmed = False

        self.owned     = PersistentMapping()
        self.want      = PersistentMapping()

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

        self.identifier  = id

        self.owners      = PersistentMapping()
        self.coveters    = PersistentMapping()

    def add_owner(self, user):
        if not isinstance(user, User):
            raise RuntimeError("that is a cabbage, not a human")
        self.owners[user.username] = user

    def add_coveter(self, user):
        if not isinstance(user, User):
            raise RuntimeError("that is a cabbage, not a human")
        self.coveters[user.username] = user


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
