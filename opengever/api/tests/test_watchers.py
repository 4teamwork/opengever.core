from collections import defaultdict
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.model import create_session
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
import json


class TestWatchersGet(SolrIntegrationTestCase):
    features = ('activity', )
    maxDiff = None

    @browsing
    def test_get_watchers_for_tasks(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.task, self.task.responsible, WATCHER_ROLE)
        browser.open(self.task.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/task-1/@watchers',
            u'referenced_users': [
                {
                    u'@id': u'http://nohost/plone/@users/%s' % self.dossier_responsible.id,
                    u'fullname': u'Ziegler Robert',
                    u'id': self.dossier_responsible.id,
                },
                {
                    u'@id': u'http://nohost/plone/@users/%s' % self.regular_user.id,
                    u'fullname': u'B\xe4rfuss K\xe4thi',
                    u'id': self.regular_user.id,
                },
            ],
            u'referenced_actors': [
                {
                    u'@id': u'http://nohost/plone/@actors/%s' % self.dossier_responsible.id,
                    u'identifier': self.dossier_responsible.id,
                },
                {
                    u'@id': u'http://nohost/plone/@actors/%s' % self.regular_user.id,
                    u'identifier': self.regular_user.id,
                },
            ],
            u'referenced_watcher_roles': [
                {
                    u'id': u'task_issuer',
                    u'title': u'Task issuer'
                },
                {
                    u'id': u'task_responsible',
                    u'title': u'Task responsible'
                },
                {
                    u'id': u'regular_watcher',
                    u'title': u'Watcher'
                }
            ],
            u'watchers_and_roles': {
                self.regular_user.id: [u'regular_watcher', u'task_responsible'],
                self.dossier_responsible.id: [u'task_issuer']
            }
        }

        self.assertDictEqual(expected_json, browser.json)

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
        center.add_watcher_to_resource(self.inbox_forwarding, self.inbox_forwarding.responsible,
                                       WATCHER_ROLE)
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1/@watchers',
            u'referenced_users': [
                {
                    u'@id': u'http://nohost/plone/@users/%s' % self.dossier_responsible.id,
                    u'fullname': u'Ziegler Robert',
                    u'id': self.dossier_responsible.id,
                },
                {
                    u'@id': u'http://nohost/plone/@users/%s' % self.regular_user.id,
                    u'fullname': u'B\xe4rfuss K\xe4thi',
                    u'id': self.regular_user.id,
                },
            ],
            u'referenced_actors': [
                {
                    u'@id': u'http://nohost/plone/@actors/%s' % self.dossier_responsible.id,
                    u'identifier': self.dossier_responsible.id,
                },
                {
                    u'@id': u'http://nohost/plone/@actors/%s' % self.regular_user.id,
                    u'identifier': self.regular_user.id,
                },
            ],
            u'referenced_watcher_roles': [
                {
                    u'id': u'task_issuer',
                    u'title': u'Task issuer'
                },
                {
                    u'id': u'task_responsible',
                    u'title': u'Task responsible'
                },
                {
                    u'id': u'regular_watcher',
                    u'title': u'Watcher'
                },
            ],
            u'watchers_and_roles': {
                self.regular_user.id: [u'regular_watcher', u'task_responsible'],
                self.dossier_responsible.id: [u'task_issuer']
            }
        }

        self.assertDictEqual(expected_json, browser.json)

        browser.open(self.inbox_forwarding, method='GET', headers=self.api_headers)

        self.assertEqual({u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1/@watchers'},
                         browser.json['@components']['watchers'])
        browser.open(self.inbox_forwarding.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['watchers'])

    @browsing
    def test_get_watchers_for_documents(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.document, self.dossier_responsible.id, WATCHER_ROLE)
        url = self.document.absolute_url() + '/@watchers'
        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': url,
            u'referenced_users': [
                {
                    u'@id': u'http://nohost/plone/@users/%s' % self.dossier_responsible.id,
                    u'fullname': u'Ziegler Robert',
                    u'id': self.dossier_responsible.id,
                }
            ],
            u'referenced_actors': [
                {
                    u'@id': u'http://nohost/plone/@actors/%s' % self.dossier_responsible.id,
                    u'identifier': self.dossier_responsible.id,
                }
            ],
            u'referenced_watcher_roles': [
                {
                    u'id': u'regular_watcher',
                    u'title': u'Watcher'
                }
            ],
            u'watchers_and_roles': {
                self.dossier_responsible.id: [u'regular_watcher']
            }
        }

        self.assertDictEqual(expected_json, browser.json)

        browser.open(self.document, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': url},
                         browser.json['@components']['watchers'])
        browser.open(self.document.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['watchers'])

    @browsing
    def test_get_watchers_for_mails(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        center.add_watcher_to_resource(self.mail_eml, self.dossier_responsible.id, WATCHER_ROLE)
        url = self.mail_eml.absolute_url() + '/@watchers'
        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': url,
            u'referenced_users': [
                {
                    u'@id': u'http://nohost/plone/@users/%s' % self.dossier_responsible.id,
                    u'fullname': u'Ziegler Robert',
                    u'id': self.dossier_responsible.id,
                }
            ],
            u'referenced_actors': [
                {
                    u'@id': u'http://nohost/plone/@actors/%s' % self.dossier_responsible.id,
                    u'identifier': self.dossier_responsible.id,
                }
            ],
            u'referenced_watcher_roles': [
                {
                    u'id': u'regular_watcher',
                    u'title': u'Watcher'
                }
            ],
            u'watchers_and_roles': {
                self.dossier_responsible.id: [u'regular_watcher']
            }
        }

        self.assertDictEqual(expected_json, browser.json)

        browser.open(self.mail_eml, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': url},
                         browser.json['@components']['watchers'])
        browser.open(self.mail_eml.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['watchers'])

    @browsing
    def test_watchers_endpoint_supports_teams(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)

        center.remove_task_responsible(self.task, self.regular_user.id)
        center.remove_task_issuer(self.task, self.dossier_responsible.id)
        center.add_task_responsible(self.task, u'team:1')

        browser.open(self.task.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        # @id for the referenced_users is not correct for teams,
        # this will have to be fixed.
        expected_json = {
            u'@id': u"{}/@watchers".format(self.task.absolute_url()),
            u'referenced_users': [
                {
                    u'@id': u'http://nohost/plone/@users/team:1',
                    u'fullname': u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                    u'id': u'team:1'
                },
            ],
            u'referenced_actors': [
                {
                    u'@id': u'http://nohost/plone/@actors/team:1',
                    u'identifier': u'team:1'
                },
            ],
            u'referenced_watcher_roles': [
                {
                    u'id': u'task_responsible',
                    u'title': u'Task responsible'
                },
            ],
            u'watchers_and_roles': {
                u'team:1': [u'task_responsible'],
            }
        }

        self.assertEqual(expected_json, browser.json)

        browser.open(self.task.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['watchers'])

    @browsing
    def test_watchers_endpoint_supports_inboxes(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)

        center.remove_task_responsible(self.task, self.regular_user.id)
        center.remove_task_issuer(self.task, self.dossier_responsible.id)

        center.add_task_responsible(self.task, u'inbox:fa')

        browser.open(self.task.absolute_url() + '/@watchers',
                     method='GET', headers=self.api_headers)

        # @id for the referenced_users is not correct for inboxes,
        # this will have to be fixed.
        expected_json = {
            u'@id': u"{}/@watchers".format(self.task.absolute_url()),
            u'referenced_users': [
                {
                    u'@id': u'http://nohost/plone/@users/inbox:fa',
                    u'fullname': u'Inbox: Finanz\xe4mt',
                    u'id': u'inbox:fa'
                },
            ],
            u'referenced_actors': [
                {
                    u'@id': u'http://nohost/plone/@actors/inbox:fa',
                    u'identifier': u'inbox:fa'
                },
            ],
            u'referenced_watcher_roles': [
                {
                    u'id': u'task_responsible',
                    u'title': u'Task responsible'
                },
            ],
            u'watchers_and_roles': {
                u'inbox:fa': [u'task_responsible'],
            }
        }

        self.assertEqual(expected_json, browser.json)

        browser.open(self.task.absolute_url() + '?expand=watchers',
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

    @browsing
    def test_get_watchers_hides_inactive_users(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)

        center.add_watcher_to_resource(self.document, self.dossier_responsible.id, WATCHER_ROLE)
        User.get(self.dossier_responsible.id).active = False

        browser.open(self.document.absolute_url() + '?expand=watchers',
                     method='GET', headers=self.api_headers)

        expected_json = {u'@id': self.document.absolute_url() + '/@watchers',
                         u'referenced_users': [],
                         u'referenced_actors': [],
                         u'referenced_watcher_roles': [],
                         u'watchers_and_roles': {}}
        self.assertEqual(expected_json, browser.json['@components']['watchers'])


class TestWatchersSolr(SolrIntegrationTestCase):
    features = ('activity', )
    maxDiff = None

    @browsing
    def test_post_watchers_for_task_adds_watcher_to_solr(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assertIsNone(solr_data_for(self.task, 'watchers'))

        browser.open(self.task.absolute_url() + '/@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.task, 'watchers'))

    @browsing
    def test_post_watchers_for_inbox_forwarding_adds_watcher_to_solr(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.assertIsNone(solr_data_for(self.inbox_forwarding, 'watchers'))

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.inbox_forwarding, 'watchers'))

    @browsing
    def test_post_watchers_for_document_adds_watcher_to_solr(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assertIsNone(solr_data_for(self.document, 'watchers'))

        browser.open(self.document, view='@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.document, 'watchers'))

    @browsing
    def test_post_watchers_for_mail_adds_watcher_to_solr(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assertIsNone(solr_data_for(self.mail_eml, 'watchers'))

        browser.open(self.mail_eml, view='@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.mail_eml, 'watchers'))

    @browsing
    def test_delete_watchers_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.task, self.regular_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.task, 'watchers'))

        browser.open(self.task.absolute_url() + '/@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertIsNone(solr_data_for(self.task, 'watchers'))

    @browsing
    def test_delete_watchers_for_inbox_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.inbox_forwarding, self.secretariat_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        self.assertEqual([self.secretariat_user.getId()],
                         solr_data_for(self.inbox_forwarding, 'watchers'))

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertIsNone(solr_data_for(self.inbox_forwarding, 'watchers'))

    @browsing
    def test_delete_watchers_for_document(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.document, self.regular_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.document, 'watchers'))

        browser.open(self.document, view='@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertIsNone(solr_data_for(self.document, 'watchers'))

    @browsing
    def test_delete_watchers_for_mail(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.mail_eml, self.regular_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        self.assertEqual([self.regular_user.getId()],
                         solr_data_for(self.mail_eml, 'watchers'))

        browser.open(self.mail_eml, view='@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        self.commit_solr()

        self.assertIsNone(solr_data_for(self.mail_eml, 'watchers'))


class TestWatchersPost(IntegrationTestCase):
    features = ('activity', )

    @browsing
    def test_post_watchers_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({self.regular_user.id: [u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         browser.json['watchers_and_roles'])
        browser.open(self.task.absolute_url() + '/@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))

        self.assertEqual(browser.status_code, 204)

        browser.open(self.task.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({self.regular_user.id: [u'regular_watcher', u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         browser.json['watchers_and_roles'])

    @browsing
    def test_post_watchers_without_data_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@watchers', method='POST',
                         headers=self.api_headers)
        self.assertEqual(
            {"message": "Property 'actor_id' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_watchers_with_invalid_actor_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@watchers',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"actor_id": "chaosqueen"}))
        self.assertEqual(
            {"message": "Actor 'chaosqueen' does not exist",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_watchers_for_inbox_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({self.regular_user.id: [u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         browser.json['watchers_and_roles'])
        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))

        self.assertEqual(browser.status_code, 204)

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers', method='GET',
                     headers=self.api_headers)
        self.assertEqual({self.regular_user.id: [u'regular_watcher', u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         browser.json['watchers_and_roles'])

    @browsing
    def test_post_watchers_for_document(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, view='@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({}, browser.json['watchers_and_roles'])
        browser.open(self.document, view='@watchers',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))

        self.assertEqual(browser.status_code, 204)

        browser.open(self.document, view='@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({self.regular_user.id: [u'regular_watcher']},
                         browser.json['watchers_and_roles'])

    @browsing
    def test_post_watchers_for_mail(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml, view='@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({}, browser.json['watchers_and_roles'])
        browser.open(self.mail_eml, view='@watchers', method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"actor_id": self.regular_user.getId()}))

        self.assertEqual(browser.status_code, 204)

        browser.open(self.mail_eml, view='@watchers', method='GET',
                     headers=self.api_headers)

        self.assertEqual({self.regular_user.id: [u'regular_watcher']},
                         browser.json['watchers_and_roles'])


class TestWatchersDelete(IntegrationTestCase):
    features = ('activity', )

    def get_watchers_and_roles(self, context):
        center = notification_center()
        watchers_and_roles = defaultdict(list)
        resource = center.fetch_resource(context)
        create_session().refresh(resource)
        for subscription in resource.subscriptions:
            watchers_and_roles[subscription.watcher.actorid].append(subscription.role)
        return watchers_and_roles

    @browsing
    def test_delete_watchers_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(self.task, self.regular_user.getId(), WATCHER_ROLE)
        watchers_and_roles = self.get_watchers_and_roles(self.task)
        self.assertEqual({self.regular_user.id: [u'regular_watcher', u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         watchers_and_roles)

        browser.open(self.task.absolute_url() + '/@watchers',
                     method='DELETE', headers=self.api_headers)

        self.assertEqual(browser.status_code, 204)
        watchers_and_roles = self.get_watchers_and_roles(self.task)
        self.assertEqual({self.regular_user.id: [u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         watchers_and_roles)

    @browsing
    def test_delete_watchers_for_inbox_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)

        watchers_and_roles = self.get_watchers_and_roles(self.inbox_forwarding)
        self.assertEqual({self.regular_user.id: [u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         watchers_and_roles)

        notification_center().add_watcher_to_resource(
            self.inbox_forwarding, self.secretariat_user.getId(), WATCHER_ROLE)

        watchers_and_roles = self.get_watchers_and_roles(self.inbox_forwarding)
        self.assertEqual({
            self.regular_user.id: [u'task_responsible'],
            self.dossier_responsible.id: [u'task_issuer'],
            self.secretariat_user.id: [u'regular_watcher']},
                         watchers_and_roles)

        browser.open(self.inbox_forwarding.absolute_url() + '/@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        watchers_and_roles = self.get_watchers_and_roles(self.inbox_forwarding)
        self.assertEqual({self.regular_user.id: [u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         watchers_and_roles)

    @browsing
    def test_delete_watchers_for_document(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.document, self.regular_user.getId(), WATCHER_ROLE)

        watchers_and_roles = self.get_watchers_and_roles(self.document)
        self.assertEqual({self.regular_user.id: [u'regular_watcher']}, watchers_and_roles)

        browser.open(self.document, view='@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        watchers_and_roles = self.get_watchers_and_roles(self.document)
        self.assertEqual({}, watchers_and_roles)

    @browsing
    def test_delete_watchers_for_mail(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.mail_eml, self.regular_user.getId(), WATCHER_ROLE)

        watchers_and_roles = self.get_watchers_and_roles(self.mail_eml)
        self.assertEqual({self.regular_user.id: [u'regular_watcher']}, watchers_and_roles)

        browser.open(self.mail_eml, view='@watchers',
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        watchers_and_roles = self.get_watchers_and_roles(self.mail_eml)
        self.assertEqual({}, watchers_and_roles)

    @browsing
    def test_delete_watchers_with_data_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        notification_center().add_watcher_to_resource(
            self.task, self.regular_user.getId(), WATCHER_ROLE)
        watchers_and_roles = self.get_watchers_and_roles(self.task)

        self.assertEqual({self.regular_user.id: [u'regular_watcher', u'task_responsible'],
                          self.dossier_responsible.id: [u'task_issuer']},
                         watchers_and_roles)

        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@watchers',
                         method='DELETE', headers=self.api_headers,
                         data=json.dumps({"actor_id": self.meeting_user.getId()}))
        self.assertEqual(
            {"message": "DELETE does not take any data",
             "type": "BadRequest"},
            browser.json)


class TestPossibleWatchers(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_get_possible_watchers_for_and_object(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        url = self.task.absolute_url() + '/@possible-watchers?query=F%C3%A4ivel'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': url,
            u'items': [{
                u'title': u'Fr\xfchling F\xe4ivel (%s)' % self.dossier_manager.getUserName(),
                u'token': self.dossier_manager.getId(),
                }],
            u'items_total': 1}

        self.assertEqual(expected_json, browser.json)

        center.add_watcher_to_resource(self.task, self.dossier_manager.getId(), WATCHER_ROLE)
        browser.open(url, method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': url,
            u'items': [],
            u'items_total': 0}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_possible_watchers_only_returns_active_users(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        url = self.task.absolute_url() + '/@possible-watchers?query=F%C3%A4ivel'

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual([self.dossier_manager.getId()],
                         [item['token'] for item in browser.json['items']])

        User.get(self.dossier_manager.getId()).active = False

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual([],
                         [item['token'] for item in browser.json['items']])

    @browsing
    def test_get_possible_watchers_for_document(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        url = self.document.absolute_url() + '/@possible-watchers?query=F%C3%A4ivel'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': url,
            u'items': [{
                u'title': u'Fr\xfchling F\xe4ivel (%s)' % self.dossier_manager.getUserName(),
                u'token': self.dossier_manager.getId(),
                }],
            u'items_total': 1}

        self.assertEqual(expected_json, browser.json)

        center.add_watcher_to_resource(self.document, self.dossier_manager.getId(), WATCHER_ROLE)
        browser.open(url, method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': url,
            u'items': [],
            u'items_total': 0}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_get_possible_watchers_for_mail(self, browser):
        center = notification_center()
        self.login(self.regular_user, browser=browser)
        url = self.mail_eml.absolute_url() + '/@possible-watchers?query=F%C3%A4ivel'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': url,
            u'items': [{
                u'title': u'Fr\xfchling F\xe4ivel (%s)' % self.dossier_manager.getUserName(),
                u'token': self.dossier_manager.getId(),
                }],
            u'items_total': 1}

        self.assertEqual(expected_json, browser.json)

        center.add_watcher_to_resource(self.mail_eml, self.dossier_manager.getId(), WATCHER_ROLE)
        browser.open(url, method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': url,
            u'items': [],
            u'items_total': 0}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.task.absolute_url() + '/@possible-watchers?b_size=5'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(5, len(browser.json.get('items')))
        self.assertEqual(20, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)
