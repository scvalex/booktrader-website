from pyramid.traversal       import resource_path

from repoze.folder           import Folder
from repoze.catalog.catalog  import Catalog
from repoze.catalog.document import DocumentMap

from urllib2                 import urlopen, URLError

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

class GoogleBooksCatalogue:
    def __init__(self):
        self.key = 'AIzaSyCwMw-h8bLntjsRydO8AXjwinfD5HnGpz4' # scvalex
        self.base_url = 'https://www.googleapis.com/books/v1/volumes'

    def query(self, qstr):
        url = "%s?q=%s" % (self.base_url, qstr)
        try:
            return unicode(urlopen(url, timeout=10).read(), "utf-8")
        except URLError, e:
            return (str(e) + ": " + url)
