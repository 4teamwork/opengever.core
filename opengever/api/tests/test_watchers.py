from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.testing import IntegrationTestCase
import json


class TestWatchersGet(IntegrationTestCase):
    features = ('activity', )

    @browsing
    def test_get_watchers_for_tasks(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.task, self.task.creators[0], TASK_ISSUER_ROLE)
        center.add_watcher_to_resource(self.task, self.task.responsible, TASK_RESPONSIBLE_ROLE)
        center.add_watcher_to_resource(self.task, self.task.responsible, WATCHER_ROLE)
        browser.open(self.task.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'watchers_and_roles': {
                u'kathi.barfuss': [u'regular_watcher', u'task_responsible'],
                u'robert.ziegler': [u'task_issuer']}}

        self.assertEqual(expected_json, browser.json)

        browser.open(self.task, method='GET', headers=self.api_headers)

        self.assertEqual({u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                  u'vertrage-und-vereinbarungen/dossier-1/task-1/@watchers'},
                         browser.json['@components']['watchers'])
        browser.open(self.task.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['watchers'])

    @browsing
    def test_get_watchers_for_inbox_forwarding(self, browser):
        center = notification_center()
        self.login(self.secretariat_user, browser=browser)
        center.add_watcher_to_resource(self.inbox_forwarding, self.inbox_forwarding.creators[0],
                                       TASK_ISSUER_ROLE)
        center.add_watcher_to_resource(self.inbox_forwarding, self.inbox_forwarding.responsible,
                                       TASK_RESPONSIBLE_ROLE)
        center.add_watcher_to_resource(self.inbox_forwarding, self.inbox_forwarding.responsible,
                                       WATCHER_ROLE)
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@watchers',
            u'watchers_and_roles': {
                u'kathi.barfuss': [u'regular_watcher', u'task_responsible'],
                u'nicole.kohler': [u'task_issuer']}}

        self.assertEqual(expected_json, browser.json)

        browser.open(self.inbox_forwarding, method='GET', headers=self.api_headers)

        self.assertEqual({u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@watchers'},
                         browser.json['@components']['watchers'])
        browser.open(self.inbox_forwarding.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['watchers'])

    @browsing
    def test_watchers_not_available_for_dossier(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(404):
            browser.open(self.dossier.absolute_url() + '/@watchers', method='GET',
                         headers=self.api_headers)
        browser.open(self.dossier, method='GET', headers=self.api_headers)
        self.assertNotIn('watchers', browser.json['@components'])


class TestWatchersPost(IntegrationTestCase):
    features = ('activity', )

    @browsing
    def test_post_watchers_for_task(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.task, self.meeting_user.getId(), TASK_RESPONSIBLE_ROLE)
        browser.open(self.task.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'watchers_and_roles': {u'herbert.jager': [u'task_responsible']}}, browser.json)
        browser.open(self.task.absolute_url() + '/@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"userid": self.meeting_user.getId()}))

        self.assertEqual(browser.status_code, 204)

        browser.open(self.task.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)
        self.assertEqual({
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'watchers_and_roles': {u'herbert.jager': [u'regular_watcher', u'task_responsible']}},
            browser.json)

    @browsing
    def test_post_watchers_without_data_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@watchers', method='POST',
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "Property 'userid' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_watchers_with_invalid_userid_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@watchers',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"userid": "chaosqueen"}))
        self.assertEqual(
            {"message": "userid 'chaosqueen' does not exist",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_watchers_for_inbox_forwarding(self, browser):
        center = notification_center()
        self.login(self.secretariat_user, browser=browser)
        center.add_watcher_to_resource(self.inbox_forwarding, self.meeting_user.getId(),
                                       TASK_RESPONSIBLE_ROLE)
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({
            u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@watchers',
            u'watchers_and_roles': {u'herbert.jager': [u'task_responsible']}},
            browser.json)
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"userid": self.meeting_user.getId()}))

        self.assertEqual(browser.status_code, 204)

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)
        self.assertEqual({
            u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@watchers',
            u'watchers_and_roles': {
                u'herbert.jager': [u'regular_watcher', u'task_responsible']}}, browser.json)


class TestWatchersDelete(IntegrationTestCase):
    features = ('activity', )

    @browsing
    def test_delete_watchers_for_task(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.task, self.regular_user.getId(), TASK_RESPONSIBLE_ROLE)
        center.add_watcher_to_resource(self.task, self.regular_user.getId(), WATCHER_ROLE)
        browser.open(self.task.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        self.assertEqual({
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'watchers_and_roles': {
                u'kathi.barfuss': [u'regular_watcher', u'task_responsible']}}, browser.json)

        browser.open(self.task.absolute_url() + '/@watchers',
                     method='DELETE', headers=self.api_headers)

        self.assertEqual(browser.status_code, 204)
        browser.open(self.task.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)
        self.assertEqual({
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'watchers_and_roles': {u'kathi.barfuss': [u'task_responsible']}}, browser.json)

    @browsing
    def test_delete_watchers_for_inbox_forwarding(self, browser):
        center = notification_center()
        self.login(self.secretariat_user, browser=browser)
        center.add_watcher_to_resource(self.inbox_forwarding, self.secretariat_user.getId(),
                                       TASK_RESPONSIBLE_ROLE)
        center.add_watcher_to_resource(self.inbox_forwarding, self.secretariat_user.getId(),
                                       WATCHER_ROLE)
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        self.assertEqual({u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@watchers',
                          u'watchers_and_roles': {
                              u'jurgen.konig': [u'regular_watcher', u'task_responsible']}},
                         browser.json)
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='DELETE', headers=self.api_headers)

        self.assertEqual(browser.status_code, 204)

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)
        self.assertEqual({
            u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@watchers',
            u'watchers_and_roles': {u'jurgen.konig': [u'task_responsible']}}, browser.json)

    @browsing
    def test_delete_watchers_with_data_raises_bad_request(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.task, self.regular_user.getId(), WATCHER_ROLE)
        browser.open(self.task.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        self.assertEqual({
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'watchers_and_roles': {
                u'kathi.barfuss': [u'regular_watcher']}}, browser.json)

        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@watchers',
                         method='DELETE', headers=self.api_headers,
                         data=json.dumps({"userid": self.meeting_user.getId()}))
        self.assertEqual(
            {"message": "DELETE does not take any data",
             "type": "BadRequest"},
            browser.json)
