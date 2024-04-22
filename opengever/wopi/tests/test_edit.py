from base64 import urlsafe_b64decode
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.testing import set_preferred_language
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi.token import validate_access_token
from plone import api
from plone.locking.interfaces import ILockable
from unittest import skip
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
            "?ui=&rs=&dchat=1&IsLicensedUser=1&WOPISrc=http://nohost"
            "/plone/wopi/files/createtreatydossiers000000000002&",
        )

        access_token = browser.css('input[name="access_token"]').first.value
        self.assertEqual(
            validate_access_token(
                urlsafe_b64decode(access_token),
                'createtreatydossiers000000000002'),
            'regular_user')

    @browsing
    def test_UI_language_is_prefered_language(self, browser):
        self.login(self.regular_user, browser=browser)
        self.enable_languages()
        browser.open()
        browser.click_on("Deutsch")

        browser.open(self.document, view="office_online_edit")

        action = browser.css("#office_form").first.get("action")
        self.assertEqual(
            action,
            "https://FFC-word-edit.officeapps.live.com/we/wordeditorframe.aspx"
            "?ui=de-DE&rs=&dchat=1&IsLicensedUser=1&WOPISrc=http://nohost"
            "/plone/wopi/files/createtreatydossiers000000000002&",
        )

    @browsing
    def test_edit_view_returns_form_action_for_non_business_users(self, browser):
        self.login(self.regular_user, browser=browser)
        api.portal.set_registry_record(name='business_user', interface=IWOPISettings, value=False)
        browser.open(self.document, view="office_online_edit")
        action = browser.css("#office_form").first.get("action")
        self.assertEqual(
            action,
            "https://FFC-word-edit.officeapps.live.com/we/wordeditorframe.aspx"
            "?ui=&rs=&dchat=1&IsLicensedUser=0&WOPISrc=http://nohost"
            "/plone/wopi/files/createtreatydossiers000000000002&",
        )

    @browsing
    def test_edit_view_returns_form_action_with_custom_base_url(self, browser):
        self.login(self.regular_user, browser=browser)
        api.portal.set_registry_record(name='base_url', interface=IWOPISettings, value=u'https://wopi.example.org/')
        browser.open(self.document, view="office_online_edit")
        action = browser.css("#office_form").first.get("action")
        self.assertEqual(
            action,
            "https://FFC-word-edit.officeapps.live.com/we/wordeditorframe.aspx"
            "?ui=&rs=&dchat=1&IsLicensedUser=1&WOPISrc=https://wopi.example.org"
            "/wopi/files/createtreatydossiers000000000002&",
        )

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
        self.assertEqual([self.regular_user.id, self.dossier_responsible.id],
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

    @browsing
    def test_edit_view_on_locked_document_redirects_to_document_and_shows_error_message(self, browser):
        self.login(self.regular_user, browser=browser)
        ILockable(self.document).lock()
        browser.open(self.document, view="office_online_edit")
        self.assertEqual(self.document.absolute_url(), browser.url)
        self.assertEqual(['Document is locked.'], error_messages())

    @browsing
    def test_edit_view_allows_frames_and_images_from_external_sources(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, view="office_online_edit")
        csp = browser.headers['Content-Security-Policy']
        self.assertIn('frame-src https:;', csp)
        self.assertIn('img-src https: data:;', csp)
