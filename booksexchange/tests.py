import unittest

from pyramid import testing

###############################################################################

# monkey-patch smtplib so we don't send actual emails
smtp  = None
inbox = []

class Message(object):
    def __init__(self, sender, recipients, message):
        self.sender     = sender
        self.recipients = recipients
        self.message    = message

class DummySMTP(object):
    def __init__(self, *args, **kwargs):
        global smtp
        smtp = self

        self.username = None
        self.password = None
        self.has_quit = False

    def login(self, username, password):
        self.username = username
        self.password = password

    def sendmail(self, sender, recipients, message):
        global inbox
        inbox.append(Message(sender, recipients, message))
        return []

    def quit(self):
        self.has_quit = True

# this is the actual monkey patch (simply replacing one class with another)
import smtplib
smtplib.SMTP     = DummySMTP
smtplib.SMTP_SSL = DummySMTP

###############################################################################

def dummy_users():
    from booksexchange.models import Users, User

    users = Users()

    user1 = User('francesco', 'f@mazzo.li', 'francesco')
    user2 = User('ciccio', 'ciccio@gmail.com', 'ciccio')

    users.new_user(user1)
    users.new_user(user2)

    return users

class UsersTests(unittest.TestCase):
    def test_new_user(self):
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq
        
        users = dummy_users()

        self.assertEqual(users['francesco'].__name__, 'francesco')
        self.assertEqual(users['francesco'].__parent__, users)
        self.assertEqual(users['francesco'].username, 'francesco')

        n, res = users.query(Eq('email', 'f@mazzo.li'))
        
        self.assertEqual(n, 1)
        self.assertEqual(res[0], users['francesco'])

    def test_update_user(self):
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq

        users = dummy_users()

        users['francesco'].email = 'e.imhotep@gmail.com'
        users.update(users['francesco'])
        
        n1, res1 = users.query(Eq('email', 'f@mazzo.li'))
        n2, res2 = users.query(Eq('email', 'e.imhotep@gmail.com'))

        self.assertEqual(n1, 0)

        self.assertEqual(n2, 1)
        self.assertEqual(res2[0], users['francesco'])

    def test_remove_user(self):
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq

        users = dummy_users()
        
        del users['francesco']
        
        self.assertFalse('francesco' in users)
        self.assertEqual(users.query(Eq('email', 'f@mazzo.li'))[0], 0)


class UserTests(unittest.TestCase):
    def _getTargetClass(self):
        from booksexchange.models import User
        return User

    def _makeOne(self):
        return self._getTargetClass()('francesco', 'f@mazzo.li', 'francesco')

    def test_user(self):
        import bcrypt
        user = self._makeOne()

        self.assertEqual(user.username, 'francesco')
        self.assertEqual(user.email, 'f@mazzo.li')
        self.assertEqual(bcrypt.hashpw('francesco', user._password), user._password)

        self.assertFalse(user.confirmed)
        
        self.assertTrue(user.check_password('francesco'))
        self.assertFalse(user.check_password('asfddsa'))

    def test_confirm(self):
        user = self._makeOne()

        tok = user.generate_token()

        self.assertFalse(user.confirm('foo'))
        self.assertFalse(user.confirmed)

        self.assertTrue(user.confirm(tok))
        self.assertTrue(user.confirmed)

    def test_adding(self):
        from exceptions import RuntimeError
        from booksexchange.models import Book
        
        user = self._makeOne()

        self.assertRaises(RuntimeError, user.add_owned, '')
        self.assertRaises(RuntimeError, user.add_want, '')
        self.assertRaises(RuntimeError, user.remove_book, '')
        self.assertRaises(RuntimeError, user.add_group, '')
        self.assertRaises(RuntimeError, user.add_message, '')
        self.assertRaises(RuntimeError, user.add_event, '')

        book1 = Book('book1', None, None, None, None, None, None, None, None)

        self.assertFalse(user.remove_book(book1))
        
        user.add_owned(book1)
        self.assertTrue(book1.identifier in user.owned)
        self.assertFalse(book1.identifier in user.want)
        self.assertTrue(user.remove_book(book1))
        self.assertFalse(book1.identifier in user.owned)

        user.add_want(book1)
        self.assertTrue(book1.identifier in user.want)
        self.assertFalse(book1.identifier in user.owned)
        self.assertTrue(user.remove_book(book1))
        self.assertFalse(book1.identifier in user.want)



###############################################################################

email_settings = {'smtp_email'    : '',
                  'smtp_server'   : '',
                  'smtp_port'     : '',
                  'smtp_username' : '',
                  'smtp_password' : '',
                  }
                  
class LoginTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from booksexchange.views import login
        return login(context, request)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_login_simple(self):
        from booksexchange.models import Users, User
        from booksexchange.views.common import HTTPFound
        
        context = Users()
        context.new_user(User('francesco', '', 'francesco'))

        request = testing.DummyRequest(params={'username'  : 'francesco',
                                               'password'  : 'francesco',
                                               'Login'     : None})
        request.referer = None

        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(context, request)

        # TODO: I have to check that remember() is called correctly
        self.assertEqual(cm.exception.status_int, 302)
        self.assertEqual(cm.exception.location, '/')
    
    def test_login_came_from(self):
        from booksexchange.models import Users, User
        from booksexchange.views.common import HTTPFound
        
        context = Users()
        context.new_user(User('francesco', '', 'francesco'))
        
        request = testing.DummyRequest(params={'username'  : 'francesco',
                                               'password'  : 'francesco',
                                               'came_from' : '/foo',
                                               'Login'     : None})
        request.referer = None


        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(context, request)

        self.assertEqual(cm.exception.status_int, 302)
        self.assertEqual(cm.exception.location, '/foo')

    def test_login_came_from_same(self):
        from booksexchange.models import Users, User
        from booksexchange.views.common import HTTPFound
        
        context = Users()
        context.new_user(User('francesco', '', 'francesco'))
        
        request = testing.DummyRequest(params={'username'  : 'francesco',
                                               'password'  : 'francesco',
                                               'came_from' : '/users/login',
                                               'Login'     : None})
        request.path = '/users/login'
        request.referer = None


        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(context, request)

        self.assertEqual(cm.exception.status_int, 302)
        self.assertEqual(cm.exception.location, '/')

    def test_login_wrong(self):
        from booksexchange.models import Users, User
        from booksexchange.views.common import HTTPFound
        
        context = Users()
        context.new_user(User('francesco', '', 'francesco'))
        
        request = testing.DummyRequest(params={'username'  : 'francesco',
                                               'password'  : 'wrong',
                                               'Login'     : None})
        request.referer = None

        res = self._callFUT(context, request)
        self.assertTrue(isinstance(res, dict))

    def test_login_already_logged(self):
        from booksexchange.models import Users, User
        from booksexchange.views.common import HTTPFound
        
        self.config.testing_securitypolicy(userid='francesco')

        context = Users()
        request = testing.DummyRequest()
        
        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(context, request)

        self.assertEqual(cm.exception.status_int, 302)


class LogoutTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from booksexchange.views import logout
        return logout(context, request)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_logout_not_logged(self):
        from booksexchange.views.common import HTTPForbidden
        
        context = None
        request = testing.DummyRequest()

        with self.assertRaises(HTTPForbidden) as cm:
            self._callFUT(context, request)

        self.assertEqual(cm.exception.status_int, 403)

    def test_logout_simple(self):
        from booksexchange.views.common import HTTPFound
        
        self.config.testing_securitypolicy(userid='francesco')

        context = None
        request = testing.DummyRequest()
        request.referer = None

        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(context, request)

        self.assertEqual(cm.exception.status_int, 302)
        self.assertEqual(cm.exception.location, '/')


    def test_logout_redirect(self):
        from booksexchange.views.common import HTTPFound

        self.config.testing_securitypolicy(userid='francesco')
        
        context = None
        request = testing.DummyRequest()
        request.referer = '/foo'

        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(context, request)

        self.assertEqual(cm.exception.status_int, 302)
        self.assertEqual(cm.exception.location, '/foo')


# class RegisterTests(unittest.TestCase):
#     def _callFUT(self, context, request):
#         from booksexchange.views import register
#         return register(context, request)

#     def setUp(self):
#         self.config = testing.setUp()

#     def tearDown(self):
#         testing.tearDown()

#     def test_register_simple(self):
#         from booksexchange.views.common import HTTPFound
        
#         context = dummy_users()

#         request = testing.DummyRequest(POST = {'_charset_'  : 'UTF-8',
#                                                '__formid__' : 'deform',
#                                                'username'   : 'foo',
#                                                '__start__'  : 'password:mapping',
#                                                'value'      : 'password',
#                                                'confirm'    : 'password',
#                                                '__end__'    : 'password:mapping',
#                                                'email'      : 'foo@foo.com',
#                                                'Register'   : 'Register'
#                                                }
#                                        )

#         with self.assertRaises(HTTPFound) as cm:
#             res = self._callFUT(context, request)
#             print res['form']

#         self.assertEqual(cm.exception.status_int, 302)
#         self.assertEqual(cm.exception.location, '/users/max/generate_token')


        
class RegistrationTokenTests(unittest.TestCase):
    def _callFUT(self, user, request):
        from booksexchange.views import registration_token
        return registration_token(user, request)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_token_normal(self):
        from booksexchange.models import User
        
        email = 'foo@gmail.com'
        user  = User('francesco', email, 'francesco')

        request                   = testing.DummyRequest()
        request.resource_url      = lambda *args, **kwargs: ''
        request.registry.settings = email_settings

        self._callFUT(user, request)

        self.assertTrue(len(inbox) > 0)
        message = inbox.pop()
        self.assertEqual(len(message.recipients), 1)
        self.assertEqual(message.recipients[0], email)
        self.assertTrue(hasattr(user, '_token'))

    def test_token_already_confirmed(self):
        from booksexchange.models import User
        from booksexchange.views.common import HTTPBadRequest

        user           = User('francesco', '', 'francesco')
        user.confirmed = True
        
        request = testing.DummyRequest()

        with self.assertRaises(HTTPBadRequest):
            self._callFUT(user, request)


class ConfirmRegistrationTests(unittest.TestCase):
    def _callFUT(self, user, request):
        from booksexchange.views import confirm_registration
        return confirm_registration(user, request)

    def test_confirm_normal(self):
        from booksexchange.models import User
        from booksexchange.views.common import HTTPFound

        user  = User('francesco', 'foo@gmail.com', 'francesco')
        token = user.generate_token()

        request = testing.DummyRequest(params = {'token':token})

        with self.assertRaises(HTTPFound) as cm:
            self._callFUT(user, request)

        self.assertTrue(user.confirmed)
        self.assertEqual(cm.exception.location, '/')

    def test_confirm_already_confirmed(self):
        from booksexchange.models import User
        from booksexchange.views.common import HTTPBadRequest

        user           = User('francesco', '', 'francesco')
        user.confirmed = True

        request = testing.DummyRequest(params = {'token':''})

        with self.assertRaises(HTTPBadRequest):
            self._callFUT(user, request)

    def test_confirm_no_token(self):
        from booksexchange.models import User
        from booksexchange.views.common import HTTPBadRequest

        user = User('francesco', '', 'francesco')

        request = testing.DummyRequest()

        with self.assertRaises(HTTPBadRequest):
            self._callFUT(user, request)
        

###############################################################################

class SearchTests(unittest.TestCase):
    def _callFUT(self, books, request):
        from booksexchange.views import search
        return search(books, request)

    def test_search_normal(self):
        from booksexchange.models import App

        request = testing.DummyRequest(params = {'query'  : 'rings',
                                                 'Search' : 'Search'})
        request.root = App()
        context = request.root['books']

        res = self._callFUT(context, request)
        self.assertTrue('form' in res)
        self.assertTrue('total_items' in res)
        self.assertTrue('result' in res)

    def test_search_json(self):
        from booksexchange.models import App
        import json

        request = testing.DummyRequest(params = {'query'  : 'rings',
                                                 'format' : 'json',
                                                 'Search' : 'Search'})
        request.root = App()
        context = request.root['books']

        res = self._callFUT(context, request)
        self.assertEqual(res.content_type, 'text/json')

        dumps = json.loads(res.body)
        self.assertTrue('status' in dumps)
        self.assertEqual(dumps['status'], 'ok')
        self.assertTrue('total_items' in dumps)
        self.assertTrue('result' in dumps)
