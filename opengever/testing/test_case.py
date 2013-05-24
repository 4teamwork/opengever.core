from lxml.cssselect import CSSSelector
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import BuilderSession
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing.z2 import Browser

import lxml.html
import transaction
import unittest2

class TestCase(unittest2.TestCase):
    pass

class FunctionalTestCase(TestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING
    use_browser = False

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.builder_session = BuilderSession.instance()
        self.builder_session.portal = self.portal

        if self.use_browser:
            self.browser = self._setup_browser()

    def tearDown(self):
        super(FunctionalTestCase, self).tearDown()
        self.builder_session.reset()

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def prepareSession(self):
        self.request = self.app.REQUEST
        if 'SESSION' not in self.request.keys():
            self.request.SESSION = {}

    def assertProvides(self, obj, interface=None):
        self.assertTrue(interface.providedBy(obj),
                        "%s should provide %s" % (obj, interface))

    """
    Browser API
    """

    def css(self, selector):
        xpath = CSSSelector(selector).path
        return self.xpath(xpath)

    def xpath(self, selector):
        html = lxml.html.fromstring(self.browser.contents)
        return html.xpath(selector)

    def assertPageContains(self, text):
        self.assertIn(text, self.browser.contents)

    def assertPageContainsNot(self, text):
        self.assertNotIn(text, self.browser.contents)

    def assertCurrentUrl(self, url):
        self.assertEquals(url, self.browser.url)

    def assertResponseStatus(self, code):
        self.assertEquals(code, self.portal.REQUEST.response.status)

    def assertResponseHeader(self, name, value):
        self.assertEquals(value, self.portal.REQUEST.response.headers.get(name))

    def _setup_browser(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        return browser
