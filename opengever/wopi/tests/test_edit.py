from base64 import urlsafe_b64decode
from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.wopi.token import validate_access_token
from zope.component import getMultiAdapter


class TestEditView(IntegrationTestCase):

    @browsing
    def test_edit_view_returns_form_with_action_and_valid_token(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, view="office_online_edit")

        action = browser.css("#office_form").first.get("action")
        self.assertEqual(
            action,
            "https://FFC-word-edit.officeapps.live.com/we/wordeditorframe.aspx"
            "?ui=de-DE&rs=de-DE&dchat=1&IsLicensedUser=0&WOPISrc=http://nohost"
            "/plone/wopi/files/createtreatydossiers000000000002&",
        )

        access_token = browser.css('input[name="access_token"]').first.value
        self.assertEqual(
            validate_access_token(
                urlsafe_b64decode(access_token),
                'createtreatydossiers000000000002'),
            'kathi.barfuss')

    @browsing
    def test_edit_view_adds_additional_collaborator_if_needed(self, browser):
        self.login(self.regular_user, browser=browser)

        # Start a collaborative editing session
        self.checkout_document(self.document, collaborative=True)

        # Second user joins
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.document, view="office_online_edit")

        # Both users should be in list of collaborators
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        self.assertEqual(['kathi.barfuss', 'robert.ziegler'],
                         manager.get_collaborators())

    @browsing
    def test_invoking_edit_view_on_exclusive_checkout_doesnt_turn_it_collaborative(self, browser):
        self.login(self.regular_user, browser=browser)

        # Start an exclusive editing session
        self.checkout_document(self.document)

        # Second user attempts to edit in Office Online
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.document, view="office_online_edit")

        # Checkout shouldn't turn into a collaborative checkout
        # because of the attempt to edit in Office Online
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        self.assertFalse(manager.is_collaborative_checkout())
        self.assertEqual([], manager.get_collaborators())
