from ftw.testbrowser import browsing
from opengever.activity.model import Notification
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
import json


class TestTransferDossierPost(IntegrationTestCase):

    @browsing
    def test_dossier_transfer_does_not_trigger_notifications(self, browser):
        self.login(self.administrator, browser=browser)
        notifications_before = Notification.query.all()

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": IDossier(self.dossier).responsible,
                          "new_userid": self.meeting_user.getId()})
                     )

        notifications_after = Notification.query.all()
        self.assertEqual(notifications_before, notifications_after)

    @browsing
    def test_transfer_dossier_without_new_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"old_userid": "kathi.barfuss"}))
        self.assertEqual(
            {"message": "Property 'new_userid' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_dossier_without_old_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"new_userid": "kathi.barfuss"}))
        self.assertEqual(
            {"message": "Property 'old_userid' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_dossier_with_invalid_new_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers, data=json.dumps(
                             {"old_userid": self.regular_user.getId(), "new_userid": "chaosqueen"}))
        self.assertEqual(
            {"message": "userid 'chaosqueen' does not exist",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_dossier_with_invalid_old_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers, data=json.dumps(
                             {"new_userid": "kathi.barfuss", "old_userid": "chaosqueen"})
                         )
        self.assertEqual(
            {"message": "userid 'chaosqueen' does not exist",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier.responsible,
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(401, browser.status_code)

    @browsing
    def test_transfer_dossier_with_identical_userids_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers, data=json.dumps(
                             {"new_userid": "kathi.barfuss", "old_userid": "kathi.barfuss"})
                         )
        self.assertEqual(
            {"message": "'old_userid' and 'new_userid' should not be the same",
             "type": "BadRequest"},
            browser.json)
