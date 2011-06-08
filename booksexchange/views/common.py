from pyramid.view           import view_config
from pyramid.traversal      import resource_path
from pyramid.exceptions     import Forbidden
from pyramid.security       import remember, forget, authenticated_userid
from pyramid.response       import Response
from pyramid.httpexceptions import (HTTPFound, HTTPForbidden,
                                    HTTPInternalServerError, HTTPBadRequest,
                                    HTTPException, HTTPRedirection,
                                    HTTPNotFound)

from repoze.catalog.query   import Eq

import colander
import deform
import json
import re

from booksexchange.models   import *
from booksexchange.schemas  import *
from booksexchange.utils    import send_email, CatalogueException




@view_config(context=HTTPRedirection)
def httpexception(context, request):
    return context


@view_config(context=App, renderer='home.mak')
def home(context, request):
    return {'events': context['events']}


@view_config(context=Forbidden)
def forbidden(request):
    if authenticated_userid(request):
        raise HTTPForbidden("You don't have enough permissions to access this page.")

    raise HTTPFound(location = request.resource_url(request.root['users'], 'login',
                                                    query={'ref':request.path}))
