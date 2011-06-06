import unittest

from pyramid import testing


class UsersTests(unittest.TestCase):
    def _getTargetClass(self):
        from booksexchange.models import Users
        return Users

    def _makeOne(self, *args):
        return self._getTargetClass()(*args)

    def test_new_user(self):
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq
        
        users = self._makeOne()

        user = User('francesco', 'f@mazzo.li', 'francesco')
        users.new_user(user)

        self.assertEqual(users['francesco'], user)
        self.assertEqual(users['francesco'].__name__, 'francesco')
        self.assertEqual(users['francesco'].__parent__, users)
        self.assertEqual(users['francesco'].username, 'francesco')

        n, res = users.query(Eq('email', 'f@mazzo.li'))
        
        self.assertEqual(n, 1)
        self.assertEqual(res[0], user)

    def test_update_user(self):
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq

        users = self._makeOne()

        user = User('francesco', 'f@mazzo.li', 'francesco')
        users.new_user(user)

        users['francesco'].email = 'e.imhotep@gmail.com'
        users.update(users['francesco'])
        
        n1, res1 = users.query(Eq('email', 'f@mazzo.li'))
        n2, res2 = users.query(Eq('email', 'e.imhotep@gmail.com'))

        self.assertEqual(n1, 0)

        self.assertEqual(n2, 1)
        self.assertEqual(res2[0], user)

    def test_remove_user(self):
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq

        users = self._makeOne()
        
        users.new_user(User('francesco', 'f@mazzo.li', 'francesco'))
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



# class ForbiddenTests(unittest.TestCase):
#     def _callFUT(self, request):
#         from booksexchange.views import forbidden
#         from booksexchange.models import appmaker
        
#         request.root = appmaker({})
        
#         return forbidden(request)

#     def test_forbidden_user(self):
#         from pyramid.testing import setUp, tearDown
        
#         self.config = setUp()
#         self.config.testing_securitypolicy(userid='francesco')

#         request = testing.DummyRequest()

#         res = self._callFUT(request)

#         self.assertEqual(res.status, '403 Forbidden')

#         tearDown(self.config)
        
#     def test_forbidden_redirect(self):
#         request = testing.DummyRequest()
        
#         res = self._callFUT(request)
        
#         self.assertEqual(res.status, '302 Found')

