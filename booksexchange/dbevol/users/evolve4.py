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

from booksexchange.models        import ac_username
from repoze.catalog.indexes.text import CatalogTextIndex
from pyramid.traversal           import resource_path

def evolve(context):
    print "Evolving Users DB to version 4..."

    if 'ac_username' not in context._catalog:
        context._catalog['ac_username'] = CatalogTextIndex(ac_username)

    for u in context:
        context._catalog.reindex_doc(
            context._docmap.docid_for_address(resource_path(context[u])), context[u])

    print "Done"
