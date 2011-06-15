from booksexchange.views.common import *

@view_config(context=App, name='debug', renderer='debug.mak')
def view_users(context, request):
    return {}
