from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import builders
from opengever.testing.browser import OGBrowser
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
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
        self.membership_tool = getToolByName(self.portal, 'portal_membership')
        if self.use_browser:
            self.browser = self._setup_browser()

    def setup_fullname(self, user_id=TEST_USER_ID, fullname=None):
        member = self.membership_tool.getMemberById(user_id)
        member.setProperties(fullname=fullname)
        transaction.commit()

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def login(self, user_id=TEST_USER_NAME):
        login(self.portal, user_id)
        return self.membership_tool.getAuthenticatedMember()

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
        terms = [term.value for term in vocabulary]
        keys.sort()
        terms.sort()
        self.assertEquals(keys, terms)

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
