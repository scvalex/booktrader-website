import datetime

from pyramid.traversal            import resource_path

from persistent                   import Persistent
from persistent.mapping           import PersistentMapping

from repoze.folder                import Folder
from repoze.catalog.catalog       import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.document      import DocumentMap

import bcrypt


class App(PersistentMapping):
    __name__   = None
    __parent__ = None

    def __init__(self):
        super(App, self).__init__()
        self['users'] = Users()


class Users(Folder):
    def __init__(self):
        super(Users, self).__init__()

        self._docmap  = DocumentMap()

        self._catalog = Catalog()
        self._catalog['email']    = CatalogFieldIndex('email')
        self._catalog['username'] = CatalogFieldIndex('username')
        
       
        self.new_user(User('francesco', 'blah@foo.com', 'friday'))

    def add(self, name, user, **kwargs):
        super(Users, self).add(name, user, **kwargs)

        # Gets the id from the docmap and updates the internal
        # catalog. Index the user in the docmap by its resource, so
        # that we can remove it when we need to.
        docid = self._docmap.add(resource_path(user))
        self._catalog.index_doc(docid, user)

    def remove(self, name, **kwargs):
        user = self[name]
        
        docid = self._docmap.docid_for_address(resource_path(user))
        self._docmap.remove_docid(docid)
        self._catalog.unindex_doc(docid)
        
        super(Users, self).remove(name, **kwargs)

    def query(self, *args, **kwargs):
        return self._catalog.query(*args, **kwargs)
    
    def new_user(self, user):
        self[user.username] = user

    def update_user(self, user):
        self._catalog.reindex_doc(self._docmap.docid_for_address(resource_url(user)),
                                  user)


class User(Persistent):
    def __init__(self, username, email, password):
        self.username = username
        self.email    = email
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.created  = datetime.datetime.utcnow()

    def check_password(self, plain_password):
        return bcrypt.hashpw(plain_password, self.password) == self.password

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root              = App()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
