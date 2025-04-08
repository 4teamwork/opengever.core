from ftw.testbrowser import browsing
from opengever.activity.model import Notification
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.resolve import LockingResolveManager
from opengever.testing import SolrIntegrationTestCase
import json


class TestTransferDossierPost(SolrIntegrationTestCase):

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
                             {"new_userid": self.regular_user.id, "old_userid": self.regular_user.id})
                         )
        self.assertEqual(
            {"message": "'old_userid' and 'new_userid' should not be the same",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_dossier_changes_responsible(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual(self.dossier_responsible.getId(),
                         IDossier(self.dossier).responsible)

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)

    @browsing
    def test_limited_admin_can_transfer_a_dossier(self, browser):
        self.login(self.limited_admin, browser=browser)

        self.assertEqual(self.dossier_responsible.getId(),
                         IDossier(self.dossier).responsible)

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)

    @browsing
    def test_transfer_dossier_changes_responsible_of_all_subdossiers(self, browser):
        self.login(self.administrator, browser=browser)

        IDossier(self.subdossier).responsible = self.dossier_responsible.getId()
        self.subdossier.reindexObject()
        self.commit_solr()

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)
        self.assertEqual(self.meeting_user.getId(), IDossier(self.subdossier).responsible)

    @browsing
    def test_transfer_dossier_changes_responsible_only_if_its_set_to_the_old_user(self, browser):
        self.login(self.administrator, browser=browser)

        IDossier(self.subdossier).responsible = self.regular_user.getId()
        self.subdossier.reindexObject()
        self.commit_solr()

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)
        self.assertEqual(self.regular_user.getId(), IDossier(self.subdossier).responsible)

    @browsing
    def test_transfer_dossier_allows_to_exclude_subdossiers(self, browser):
        self.login(self.administrator, browser=browser)

        IDossier(self.subdossier).responsible = self.dossier_responsible.getId()
        self.subdossier.reindexObject()
        self.commit_solr()

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId(),
                          "recursive": False}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)
        self.assertEqual(self.dossier_responsible.getId(), IDossier(self.subdossier).responsible)

    @browsing
    def test_transfer_dossier_is_only_allowed_for_not_resolved_dossiers(self, browser):
        self.login(self.administrator, browser=browser)

        LockingResolveManager(self.resolvable_dossier).resolve()

        with browser.expect_http_error(400):
            browser.open(self.resolvable_dossier.absolute_url() + '/@transfer-dossier', method='POST',
                         headers=self.api_headers, data=json.dumps(
                             {"old_userid": self.dossier_responsible.getId(),
                              "new_userid": self.meeting_user.getId()}))

        self.assertEqual(
            {"message": "Only open dossiers can be transfered to another user",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_subdossiers_will_skip_resolved_dossiers(self, browser):
        self.login(self.administrator, browser=browser)

        IDossier(self.subdossier).responsible = self.dossier_responsible.getId()
        self.subdossier.reindexObject()
        LockingResolveManager(self.subdossier).resolve()
        self.commit_solr()

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)
        self.assertEqual(self.dossier_responsible.getId(), IDossier(self.subdossier).responsible)

    @browsing
    def test_transfer_dossier_changes_responsible_extract_token_from_old_user(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual(self.dossier_responsible.getId(),
                         IDossier(self.dossier).responsible)

        old_userid = {
            u'token': self.dossier_responsible.getId(),
            u'title': self.dossier_responsible.getUserName()
        }

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": old_userid,
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)
