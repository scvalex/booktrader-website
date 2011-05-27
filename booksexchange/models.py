import datetime

from pyramid.traversal            import resource_path

from persistent                   import Persistent
from persistent.mapping           import PersistentMapping

from repoze.catalog.indexes.field import CatalogFieldIndex

from booksexchange.utils          import IndexFolder

import bcrypt

class App(PersistentMapping):
    __name__   = None
    __parent__ = None

    def __init__(self):
        super(App, self).__init__()
        self['users'] = Users()
        self['books'] = Books()


class Users(IndexFolder):
    def __init__(self):
        super(Users, self).__init__(email    = CatalogFieldIndex('email'),
                                    username = CatalogFieldIndex('username'))
       
        self.new_user(User('francesco', 'blah@foo.com', 'friday'))

    def new_user(self, user):
        self[user.username] = user


class User(Persistent):
    def __init__(self, username, email, password):
        self.username = username
        self.email    = email
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.created  = datetime.datetime.utcnow()

    def check_password(self, plain_password):
        return bcrypt.hashpw(plain_password, self.password) == self.password

class Books(IndexFolder):
    def __init__(self):
        super(Books, self).__init__(isbn = CatalogFieldIndex('isbn'))

class Book(Persistent):
    def __init__(self, title, subtitle, authors, publisher, isbn, description):
        self.title       = title
        self.subtitle    = subtitle
        self.authors     = authors
        self.publisher   = publisher
        self.isbn        = isbn
        self.description = description

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root              = App()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
