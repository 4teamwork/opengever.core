from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
import transaction
import unittest2

class TestCase(unittest2.TestCase):
    pass

class FunctionalTestCase(TestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING
    use_browser = False

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

        if self.use_browser:
            self.browser = self._setup_browser()

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()


    """
    Browser API
    """

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
