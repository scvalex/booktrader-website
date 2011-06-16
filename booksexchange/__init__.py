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

from pyramid.config         import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization  import ACLAuthorizationPolicy
from pyramid.session        import UnencryptedCookieSessionFactoryConfig
from pyramid.httpexceptions import HTTPException, HTTPInternalServerError

from repoze.zodbconn.finder import PersistentApplicationFinder

from booksexchange.models   import appmaker
from booksexchange.security import groupfinder
from booksexchange.utils    import AppRequest, catch_exc

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    authn_policy = AuthTktAuthenticationPolicy(secret=settings.get('auth_secret'),
                                               callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    session_fac  = UnencryptedCookieSessionFactoryConfig(settings.get('session_secret'))

    zodb_uri = settings.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError("No 'zodb_uri' in application configuration.")

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)

    config = Configurator(root_factory          = get_root,
                          settings              = settings,
                          authentication_policy = authn_policy,
                          authorization_policy  = authz_policy,
                          session_factory       = session_fac)

    config.set_request_factory(AppRequest)

    config.add_static_view('static', 'booksexchange:static')
    config.add_static_view('deform', 'deform:static')

    config.add_renderer('.mak', 'booksexchange.utils.app_renderer_factory')
    config.add_renderer('.mako', 'booksexchange.utils.app_renderer_factory')

    config.scan('booksexchange.views')

    pyr_app      = config.make_wsgi_app()
    app          = catch_exc(pyr_app)
    app.registry = pyr_app.registry
    return app
