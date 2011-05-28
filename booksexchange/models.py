import datetime

from pyramid.security             import Allow, Everyone
from pyramid.traversal            import resource_path

from persistent                   import Persistent
from persistent.mapping           import PersistentMapping

from repoze.catalog.indexes.field import CatalogFieldIndex

from booksexchange.utils          import IndexFolder, GoogleBooksCatalogue

import bcrypt
import hashlib
import uuid

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

    def add_book(self, book):
        self.owned[book.identifier] = book
    

class Books(IndexFolder):
    def __init__(self):
        super(Books, self).__init__(isbn = CatalogFieldIndex('isbn'))

        self.catalogue = GoogleBooksCatalogue()

    def new_book(self, book):
        self[book.identifier] = book


class Book(Persistent):
    def __init__(self, title, subtitle, authors, publisher, date,
                 identifiers, description):
        self.title       = title
        self.subtitle    = subtitle
        self.authors     = authors
        self.publisher   = publisher
        self.year        = date
        if isinstance(self.year, basestring):
            self.year = int(self.year[:4])
        self.identifiers = identifiers
        self.description = description

        self.googleId    = None
        self.identifier  = self.make_identifier()

    def make_identifier(self):
        m = hashlib.new("sha1")
        m.update(self.recode(self.title))
        m.update(self.recode(self.subtitle))
        m.update(self.recode(self.publisher))
        m.update(str(self.year))

        return m.hexdigest()

    def recode(self, s):
        return s.encode('ascii', 'backslashreplace')


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
