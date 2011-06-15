from booksexchange.views.common import *

@view_config(context=App, name='about', renderer='about.mak')
def view_users(context, request):
    return {}
