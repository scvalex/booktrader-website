import datetime

from pyramid.traversal            import resource_path

from persistent                   import Persistent
from persistent.mapping           import PersistentMapping

from repoze.catalog.indexes.field import CatalogFieldIndex

from booksexchange.utils          import IndexFolder

import bcrypt
import uuid

class App(PersistentMapping):
    __name__   = None
    __parent__ = None

    def setchild(self, name, obj):
        self[name]     = obj
        obj.__name__   = name
        obj.__parent__ = self
    
    def __init__(self):
        super(App, self).__init__()
        self.setchild('users', Users())


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
    
def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root              = App()
        zodb_root['app_root'] = app_root

        app_root['users'].new_user(User('francesco', 'f@mazzo.li', 'francesco'))
        app_root['users']['francesco'].confirmed = True
        
        import transaction
        transaction.commit()
    return zodb_root['app_root']
