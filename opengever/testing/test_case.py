from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing.browser import OGBrowser
from opengever.testing.builders import BuilderSession
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles

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
    Vocabulary assert helpers
    """

    def assertTerms(self, expected_terms, vocabulary):
        effective_terms = []
        for term in list(vocabulary):
            effective_terms.append((term.value, term.title))

        self.assertEquals(expected_terms, effective_terms)

    def assertTermKeys(self, keys, vocabulary):
        self.assertEquals(keys, [term.value for term in vocabulary])

    def assertInTerms(self, value, vocabulary):
        self.assertIn(value, [term.value for term in vocabulary])

    def assertNotInTerms(self, value, vocabulary):
        self.assertNotIn(value, [term.value for term in vocabulary])

    """
    Browser API
    Deprecated, please don't extend this API and use
    opengever.testing.browser whenever possible.
    """

    def assertPageContains(self, text):
        self.assertIn(text, self.browser.contents)

    def assertPageContainsNot(self, text):
        self.assertNotIn(text, self.browser.contents)

    def assertResponseStatus(self, code):
        self.assertEquals(code, self.portal.REQUEST.response.status)

    def assertResponseHeader(self, name, value):
        self.assertEquals(value, self.portal.REQUEST.response.headers.get(name))

    def _setup_browser(self):
        browser = OGBrowser(self.app)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        return browser
