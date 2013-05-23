from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter


class TestLogoutOverlayWithoutCheckouts(FunctionalTestCase):

    def setUp(self):
        super(TestLogoutOverlayWithoutCheckouts, self).setUp()
        self.grant('Manager')
        self.document = Builder("document").create()

    def test_logout_is_handled_using_a_js_script(self):
        view = self.portal.restrictedTraverse('@@logout_overlay')
        self.assertEquals("empty:./logout", view())

class TestLogoutOverlayWithCheckouts(FunctionalTestCase):

    def setUp(self):
        super(TestLogoutOverlayWithCheckouts, self).setUp()
        self.grant('Manager')

        self.checkout1 = Builder("document").titled("About Plone").create()
        self.document = Builder("document").titled("NOT checkedout").create()
        self.checkout2 = Builder("document").titled("About Python").create()
        getMultiAdapter(
            (self.checkout1, self.portal.REQUEST),
            ICheckinCheckoutManager).checkout()

        getMultiAdapter(
            (self.checkout2, self.portal.REQUEST),
            ICheckinCheckoutManager).checkout()

    def test_contains_links_to_checked_out_documents(self):
        view = self.portal.restrictedTraverse('@@logout_overlay')()
        self.assertIn('<a target="_blank" href="http:' \
            '//nohost/plone/document-1">About Plone</a>', view)
        self.assertIn('<a target="_blank" href="http:' \
            '//nohost/plone/document-3">About Python</a>', view)

    def test_contains_hidden_field_with_redirect_url(self):
        view = self.portal.restrictedTraverse('@@logout_overlay')()
        self.assertIn('<input type="hidden" name="form.redirect.url" ' \
            'value="./logout" />', view)
