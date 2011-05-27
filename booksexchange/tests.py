import unittest

from pyramid import testing


class UsersTests(unittest.TestCase):
    def _getTargetClass(self):
        from booksexchange.models import Users
        return Users

    def _makeOne(self, *args):
        return self._getTargetClass()(*args)

    def test_new_user(self):
        users = self._makeOne()
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq
        
        users.new_user(User('francesco', '', 'francesco'))

        self.assertEqual(users['francesco'].__name__, 'francesco')
        self.assertEqual(users['francesco'].__parent__, users)
        self.assertEqual(users['francesco'].username, 'francesco')
        self.assertEqual(users.query(Eq('username', 'francesco'))[0], 1)
        self.assertEqual(users.query(NotEq('username', 'francesco'))[0], 0)

    def test_update_user(self):
        users = self._makeOne()
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq
        
        user = User('francesco', '', 'francesco')
        users.new_user(User('francesco', '', 'francesco'))
        users['francesco'].username = 'max'
        users.update(users['francesco'])
        
        # Note that the __name__ doesn't change, which is the expected behaviour
        self.assertEqual(users['francesco'].username, 'max')
        self.assertEqual(users.query(Eq('username', 'francesco'))[0], 0)
        self.assertEqual(users.query(Eq('username', 'max'))[0], 1)
        self.assertEqual(users.query(NotEq('username', 'max'))[0], 0)

    def test_remove_user(self):
        users = self._makeOne()
        from booksexchange.models import User
        from repoze.catalog.query import Eq, NotEq
        
        user = User('francesco', '', 'francesco')
        users.new_user(User('francesco', '', 'francesco'))
        del users['francesco']
        
        self.assertFalse('francesco' in users)
        self.assertEqual(users.query(Eq('username', 'francesco'))[0], 0)
        self.assertEqual(users.query(NotEq('username', 'francesco'))[0], 0)


class UserTests(unittest.TestCase):
    def _getTargetClass(self):
        from booksexchange.models import User
        return User

    def _makeOne(self):
        return self._getTargetClass()('francesco', 'foo@bar.com', 'friday')

    def test_user(self):
        import bcrypt
        user = self._makeOne()
        self.assertEqual(user.username, 'francesco')
        self.assertEqual(user.email, 'foo@bar.com')
        self.assertEqual(bcrypt.hashpw('friday', user._password), user._password)
    
            
class LoginTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from booksexchange.views import login
        return login(context, request)

    def test_notlogged(self):
        from pyramid.url import resource_url
        from pyramid.security import authenticated_userid
        
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.subpath = ['users', 'login']
        
        res = self._callFUT(context, request)

        if authenticated_userid(request):
            self.assertEqual(res.status, '302 Found')
        else:
            self.assertIn('came_from', res)
            self.assertIn('username', res)
    
    def test_logged_correct(self):
        from booksexchange.models import Users, User
        context = Users()
        context.new_user(User('francesco', 'none', 'francesco'))
        
        request = testing.DummyRequest(params={'username'       : 'francesco',
                                               'password'       : 'francesco',
                                               'form.submitted' : True})
        request.subpath = ['users', 'login']
        
        res = self._callFUT(context, request)

        # Right now I'm just checking that when the login is correct,
        # it redirects, but that's not quite right. I don't know how
        # to easily verify that the userid has been remembered from
        # the response, and not from the request.

        self.assertEqual(res.status, '302 Found')

    def test_logged_wrong(self):
        from booksexchange.models import Users, User
        context = Users()
        context.new_user(User('francesco', 'none', 'francesco'))
        
        request = testing.DummyRequest(params={'username'       : 'francesco',
                                               'password'       : 'wrong',
                                               'form.submitted' : True})
        request.subpath = ['users', 'login']
        
        res = self._callFUT(context, request)

        self.assertTrue(not ('status' in res) or res.status != '302 Found')


class ForbiddenTests(unittest.TestCase):
    def _callFUT(self, request):
        from booksexchange.views import forbidden
        from booksexchange.models import appmaker
        
        request.root = appmaker({})
        
        return forbidden(request)

    def test_forbidden_user(self):
        from pyramid.testing import setUp, tearDown
        
        self.config = setUp()
        self.config.testing_securitypolicy(userid='francesco')

        request = testing.DummyRequest()

        res = self._callFUT(request)

        self.assertEqual(res.status, '403 Forbidden')

        tearDown(self.config)
        
    def test_forbidden_redirect(self):
        request = testing.DummyRequest()
        
        res = self._callFUT(request)
        
        self.assertEqual(res.status, '302 Found')

