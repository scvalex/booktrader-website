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

from booksexchange.models        import ac_group_name
from repoze.catalog.indexes.text import CatalogTextIndex

def evolve(context):
    print "Evolving Groups DB to version 2..."

    if 'ac_name' not in context._catalog:
        context._catalog['ac_name'] = CatalogTextIndex(ac_group_name)

    for g in context:
        context._catalog.reindex_doc(
            context._docmap.docid_for_address(resource_path(context[g])), context[g])

    print "Done"
