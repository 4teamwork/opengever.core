from opengever.base.interfaces import IRedirector
from opengever.base.redirector import REDIRECTOR_COOKIE_NAME
from opengever.base.redirector import RedirectorCookie
from opengever.base.redirector import RedirectorViewlet
from opengever.testing import FunctionalTestCase


class TestRedirectorCookie(FunctionalTestCase):

    def test_adding_string_to_cookie(self):
        self.assertEquals([], RedirectorCookie(self.request).read())
        RedirectorCookie(self.request).add({'foo': 'one'})
        RedirectorCookie(self.request).add({'foo': 'two'})
        self.assertEquals([{'foo': 'one'}, {'foo': 'two'}],
                          RedirectorCookie(self.request).read())
        self.assertEquals([], RedirectorCookie(self.request).read())

    def test_read_remove_flag(self):
        RedirectorCookie(self.request).add({'foo': 'one'})
        self.assertEquals([{'foo': 'one'}],
                          RedirectorCookie(self.request).read(remove=False))
        self.assertEquals([{'foo': 'one'}],
                          RedirectorCookie(self.request).read())
        self.assertEquals([], RedirectorCookie(self.request).read())

    def test_cookie_is_set(self):
        self.assertEquals(None, self.get_cookie())

        RedirectorCookie(self.request).add({'foo': 'one'})
        self.assertEquals({'quoted': True,
                           'value': '[{"foo": "one"}]',
                           'path': '/'},
                          self.get_cookie())

        RedirectorCookie(self.request).add({'foo': 'two'})
        self.assertEquals({'quoted': True,
                           'value': '[{"foo": "one"}, {"foo": "two"}]',
                           'path': '/'},
                          self.get_cookie())

    def test_cookie_is_invalidated(self):
        RedirectorCookie(self.request).add({'foo': 'one'})
        self.assertEquals({'quoted': True,
                           'value': '[{"foo": "one"}]',
                           'path': '/'},
                          self.get_cookie())

        RedirectorCookie(self.request).read()
        self.assertEquals({'quoted': True,
                           'max_age': 0,
                           'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
                           'value': 'deleted',
                           'path': '/'},
                          self.get_cookie())

    def get_cookie(self):
        return self.request.response.cookies.get(REDIRECTOR_COOKIE_NAME, None)


class TestRedirector(FunctionalTestCase):

    def setUp(self):
        super(TestRedirector, self).setUp()
        self.prepareSession()

        self.redirector = IRedirector(self.request)

    def test_stores_and_retrieves_redirects(self):
        self.redirector.redirect('http://www.google.ch', target='named-window')
        self.assertEquals([{'url': 'http://www.google.ch',
                            'target': 'named-window',
                            'timeout': 0}],
                          self.redirector.get_redirects())

    def test_retrieving_a_redirect_removes_it(self):
        self.redirector.redirect('http://www.ebay.ch', target='named-window')

        self.assertEquals(1, len(self.redirector.get_redirects()))
        self.assertEquals(0, len(self.redirector.get_redirects()))

    def test_pass_remove_false_to_keeps_redirects(self):
        self.redirector.redirect('http://www.yahoo.com', target='named-window')

        self.assertEquals(1, len(self.redirector.get_redirects(remove=False)))
        self.assertEquals(1, len(self.redirector.get_redirects(remove=False)))

class TestRedirectorViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestRedirectorViewlet, self).setUp()
        self.prepareSession()

    def test_viewlet_only_redirects_once(self):
        redirector = IRedirector(self.request)
        redirector.redirect('http://www.google.ch', target='named-window')

        viewlet = RedirectorViewlet(self.portal, self.request, {}, {})
        self.assertIn("http://www.google.ch", viewlet.render().strip())

        self.assertEquals("", viewlet.render())
