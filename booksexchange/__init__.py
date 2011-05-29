from pyramid.config         import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization  import ACLAuthorizationPolicy
from pyramid.session        import UnencryptedCookieSessionFactoryConfig
from pyramid.httpexceptions import HTTPException, HTTPInternalServerError

from repoze.zodbconn.finder import PersistentApplicationFinder

from booksexchange.models   import appmaker
from booksexchange.security import groupfinder
from booksexchange.utils    import AppRequest
from booksexchange.views    import httpexception

class SuperSpecial(object):
    """ Exception capturing middleware"""

    def __init__(self, application):
        self.app = application

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except HTTPException, e:
            print "Exception: ", e
            return e # httpexception(e, None)

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
    
    config.scan('booksexchange')
    return config.make_wsgi_app()
