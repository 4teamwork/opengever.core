from base64 import urlsafe_b64decode
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.wopi.token import validate_access_token


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
