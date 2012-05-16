from opengever.document.testing import OPENGEVER_DOCUMENT_INTEGRATION_TESTING
from unittest2 import TestCase
from Products.CMFCore.utils import getToolByName
from plone.app.testing import setRoles, TEST_USER_ID
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import getMultiAdapter


class TestLogoutOverlay(TestCase):

    layer = OPENGEVER_DOCUMENT_INTEGRATION_TESTING

    def setUp(self):

        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.mtool = getToolByName(self.portal, 'portal_membership')

        self.portal.invokeFactory('opengever.document.document', 'document1')
        self.d1 = self.portal['document1']

        self.portal.invokeFactory('opengever.document.document', 'document2')
        self.d2 = self.portal['document2']

        self.portal.invokeFactory('opengever.document.document', 'document3')
        self.d3 = self.portal['document3']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_no_checkouts(self):
        """ We have no checkouts. So the logout is handled over the
        js script
        """
        view = self.portal.restrictedTraverse('@@logout_overlay')()

        self.assertEquals(view, 'empty')

    def test_with_checkouts(self):
        """ We have checkouts, so we return the view with links to the
        checked out documents
        """
        getMultiAdapter(
            (self.d1, self.portal.REQUEST),
            ICheckinCheckoutManager).checkout()

        getMultiAdapter(
            (self.d3, self.portal.REQUEST),
            ICheckinCheckoutManager).checkout()

        view = self.portal.restrictedTraverse('@@logout_overlay')()

        self.assertIn('<a target="_blank" href="http:' \
            '//nohost/plone/document1">document1</a>', view)

        self.assertIn('<a target="_blank" href="http:' \
            '//nohost/plone/document3">document3</a>', view)

    def test_redirect_after_logout(self):
        """ The user pushed the logout button in the overlay
        """
        getMultiAdapter(
            (self.d3, self.portal.REQUEST),
            ICheckinCheckoutManager).checkout()

        self.request.form['form.submitted'] = 'Logout'

        view = self.portal.restrictedTraverse('@@logout_overlay')()

        self.assertEquals(view, './logout')
