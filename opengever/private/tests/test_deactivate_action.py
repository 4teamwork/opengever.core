from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
import unittest


class TestDeleteActionInPrivateFolderTabbedViews(IntegrationTestCase):

    @browsing
    def test_deactivate_action_is_not_displayed_for_administrator(self, browser):
        self.login(self.member_admin, browser)
        browser.open(self.private_dossier)
        statusmessages.assert_no_error_messages()

        self.assertEquals(
            0,
            len(browser.css('#workflow-transition-dossier-transition-deactivate')))

    @browsing
    def test_deactivate_action_is_not_displayed_for_owner(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_dossier)
        statusmessages.assert_no_error_messages()

        self.assertEquals(
            0,
            len(browser.css('#workflow-transition-dossier-transition-deactivate')))
