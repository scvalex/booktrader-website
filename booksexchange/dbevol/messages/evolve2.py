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

from persistent.list import PersistentList
from booksexchange.models import Offer

def evolve(context):
    print "Evolving Messages DB to version 2...",
    for m in context.values():
        if isinstance(m, Offer):
            print ".",
            m.accepted = PersistentList()
    print "Done"
    context.evolved = 2
