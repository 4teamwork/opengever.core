from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IRedirector
from opengever.base.redirector import REDIRECTOR_COOKIE_NAME
from opengever.base.redirector import RedirectorCookie
from opengever.base.redirector import RedirectorViewlet
from opengever.testing import IntegrationTestCase
from plone.app.caching.interfaces import IETagValue
from zope.component import getMultiAdapter
import hashlib
import json


class TestRedirectorCookie(IntegrationTestCase):

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


class TestRedirector(IntegrationTestCase):

    def setUp(self):
        super(TestRedirector, self).setUp()
        self.redirector = IRedirector(self.request)

    def test_stores_and_retrieves_redirects(self):
        self.redirector.redirect('http://example.com', target='named-window')
        self.assertEquals([{'url': 'http://example.com',
                            'target': 'named-window',
                            'timeout': 0}],
                          self.redirector.get_redirects())

    def test_retrieving_a_redirect_removes_it(self):
        self.redirector.redirect('http://example.com', target='named-window')

        self.assertEquals(1, len(self.redirector.get_redirects()))
        self.assertEquals(0, len(self.redirector.get_redirects()))

    def test_pass_remove_false_to_keeps_redirects(self):
        self.redirector.redirect('http://example.com', target='named-window')

        self.assertEquals(1, len(self.redirector.get_redirects(remove=False)))
        self.assertEquals(1, len(self.redirector.get_redirects(remove=False)))

class TestRedirectorViewlet(IntegrationTestCase):

    def test_viewlet_only_redirects_once(self):
        redirector = IRedirector(self.request)
        redirector.redirect('http://example.com', target='named-window')

        viewlet = RedirectorViewlet(self.portal, self.request, {}, {})
        self.assertIn("http://example.com", viewlet.render().strip())

        self.assertEquals("", viewlet.render())

    def test_etag_value_is_md5_hash_of_cookie_content(self):
        document = create(Builder('document'))
        url = 'http://nohost/plone/document-1/externaledit'
        target = 'named-window'

        self.assertIsNone(self.get_etag_value_for(document))

        # register redirect
        redirector = IRedirector(self.request)
        redirector.redirect(url, target=target)

        data = json.dumps([{'url': url, 'target': target, 'timeout': 0}])
        m = hashlib.md5()
        m.update(data.encode('utf-8'))
        expected_hash = m.hexdigest()

        self.assertEquals(expected_hash,
                          self.get_etag_value_for(document))

        # Read and delete redirect
        viewlet = RedirectorViewlet(self.portal, self.request, {}, {})
        viewlet.render()

        self.assertIsNone(self.get_etag_value_for(document))

    def get_etag_value_for(self, document):
        view = document.unrestrictedTraverse('@@tabbed_view')
        adapter = getMultiAdapter((view, self.request),
                                  IETagValue,
                                  name='redirector')
        return adapter()
