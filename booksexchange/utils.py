from pyramid.traversal       import resource_path

from repoze.folder           import Folder
from repoze.catalog.catalog  import Catalog
from repoze.catalog.document import DocumentMap

class IndexFolder(Folder):
    def __init__(self, **kwargs):
        super(IndexFolder, self).__init__()

        self._docmap = DocumentMap()

        self._catalog = Catalog()
        
        for k, v in kwargs.iteritems():
            self._catalog[k] = v

    def add(self, name, obj, *args, **kwargs):
        super(IndexFolder, self).add(name, obj, *args, **kwargs)

        docid = self._docmap.add(resource_path(obj))
        self._catalog.index_doc(docid, obj)

    def remove(self, name, *args, **kwargs):
        obj = self[name]
        
        docid = self._docmap.docid_for_address(resource_path(obj))
        self._docmap.remove_docid(docid)
        self._catalog.unindex_doc(docid)
        
        super(Users, self).remove(name, *args, **kwargs)

    def query(self, *args, **kwargs):
        return self._catalog.query(*args, **kwargs)

    def update(self, obj):
        self._catalog.reindex_doc(self._docmap.docid_for_address(resource_url(obj)),
                                  obj)

