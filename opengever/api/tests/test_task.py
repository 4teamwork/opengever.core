from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.response import IResponseContainer
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.ogds.base.Extensions.plugins import activate_request_layer
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.restapi.serializer.converters import json_compatible
from zope.component import getMultiAdapter
import json


class TestTaskSerialization(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_task_contains_a_list_of_responses(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.maxDiff = None
        responses = browser.json['responses']
        self.assertEquals(2, len(responses))
        self.assertEquals(
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/@responses/1472652213000000',
             u'added_objects': [
                 {u'@id': self.subtask.absolute_url(),
                  u'@type': u'opengever.task.task',
                  u'description': u'',
                  u'is_leafnode': None,
                  u'review_state': u'task-state-resolved',
                  u'title': self.subtask.title}
             ],
             u'changes': [],
             u'created': json_compatible(self.subtask.created().utcdatetime()),
             u'creator': {u'title': u'Ziegler Robert', u'token': u'robert.ziegler'},
             u'mimetype': u'',
             u'related_items': [],
             u'rendered_text': u'',
             u'response_id': 1472652213000000,
             u'response_type': u'default',
             u'successor_oguid': u'',
             u'text': u'',
             u'transition': u'transition-add-subtask'},
            responses[0])

    @browsing
    def test_task_response_contains_changes(self, browser):
        # Modify deadline to have a response containing field changes
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'Response': 'Nicht mehr dringend',
                      'New Deadline': '1.1.2023'})
        browser.click_on('Save')

        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)

        response = browser.json['responses'][-1]
        self.assertEquals(
            self.dossier_responsible.id, response['creator'].get('token'))
        self.assertEquals(
            u'task-transition-modify-deadline', response['transition'])
        self.assertEquals(
            [{u'field_id': u'deadline', u'field_title': u'Deadline',
              u'after': u'2023-01-01', u'before': u'2016-11-01'}],
            response['changes'])

    @browsing
    def test_response_key_contains_empty_list_for_task_without_responses(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.inbox_task, method="GET", headers=self.api_headers)
        self.assertEquals([], browser.json['responses'])

    @browsing
    def test_fowardings_contains_a_list_of_responses(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(
            self.inbox_forwarding, method="GET", headers=self.api_headers)
        self.assertEquals(
            [{u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/@responses/1472634453000000',
              u'response_id': 1472634453000000,
              u'response_type': u'default',
              u'added_objects': [{
                u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/document-13',
                u'@type': u'opengever.document.document',
                u'description': u'',
                u'is_leafnode': None,
                u'review_state': u'document-state-draft',
                u'title': u'Dokument im Eingangsk\xf6rbliweiterleitung'}],
              u'changes': [],
              u'creator': {
                  u'token': u'nicole.kohler',
                  u'title': u'Kohler Nicole'},
              u'created': u'2016-08-31T11:07:33',
              u'related_items': [],
              u'text': u'',
              u'mimetype': u'',
              u'successor_oguid': u'',
              u'rendered_text': u'',
              u'transition': u'transition-add-document'}],
            browser.json['responses'])

    @browsing
    def test_adding_a_response_sucessful(self, browser):
        self.login(self.regular_user, browser=browser)

        current_responses_count = len(IResponseContainer(self.task))

        with freeze(datetime(2016, 12, 9, 9, 40)):
            url = '{}/@responses'.format(self.task.absolute_url())
            browser.open(url, method="POST", headers=self.api_headers,
                         data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        self.assertEquals(current_responses_count + 1,
                          len(IResponseContainer(self.task)))

        self.assertEquals(201, browser.status_code)
        self.maxDiff = None
        self.assertEquals(
            {u'@id': '{}/@responses/1481272800000000'.format(self.task.absolute_url()),
             'response_id': 1481272800000000,
             'response_type': 'comment',
             u'created': u'2016-12-09T09:40:00',
             u'changes': [],
             u'creator': {
                 u'token': self.regular_user.id,
                 u'title': u'B\xe4rfuss K\xe4thi'},
             u'text': u'Angebot \xfcberpr\xfcft',
             u'transition': u'task-commented',
             u'successor_oguid': u'',
             u'rendered_text': u'',
             u'related_items': [],
             u'mimetype': u'',
             u'added_objects': []},
            browser.json)

    @browsing
    def test_containing_dossier_for_task_within_dossier(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.maxDiff = None
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',  # noqa
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json['containing_dossier']
        )

    @browsing
    def test_containing_dossier_for_task_within_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        task_in_subdossier = create(Builder('task')
                                    .within(self.subdossier)
                                    .having(
                                        responsible_client='fa',
                                        responsible=self.regular_user.getId(),
                                        issuer=self.dossier_responsible.getId(),
                                    ))
        browser.open(task_in_subdossier, method="GET", headers=self.api_headers)
        self.maxDiff = None
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json['containing_dossier']
        )

    @browsing
    def test_containing_dossier_for_subtask(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.subtask, method="GET", headers=self.api_headers)
        self.maxDiff = None
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',  # noqa
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json['containing_dossier']
        )

    @browsing
    def test_containing_dossier_for_inbox_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(self.inbox_forwarding, method="GET", headers=self.api_headers)
        self.maxDiff = None
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/eingangskorb',
                u'@type': u'opengever.inbox.inbox',
                u'description': u'',
                u'is_leafnode': None,
                u'review_state': u'inbox-state-default',
                u'title': u'Eingangsk\xf6rbli',
            },
            browser.json['containing_dossier']
        )

    @browsing
    def test_task_response_contains_items(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.maxDiff = None
        self.assertEqual(
            [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                            u'dossier-1/task-1/task-2',
                    u'@type': u'opengever.task.task',
                    u'description': u'',
                    u'is_leafnode': None,
                    u'review_state': u'task-state-resolved',
                    u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'},
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                            u'dossier-1/task-1/document-35',
                    u'@type': u'opengever.document.document',
                    u'description': u'',
                    u'is_leafnode': None,
                    u'review_state': u'document-state-draft',
                    u'title': u'Feedback zum Vertragsentwurf'
                }
            ],
            browser.json['items']
        )


class TestTaskCommentSync(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def test_comment_will_be_synced(self):
        self.grant('Manager')

        predecessor = create(Builder('task'))
        successor = create(Builder('task').successor_from(predecessor))

        activate_request_layer(self.portal.REQUEST,
                               IInternalOpengeverRequestLayer)

        successor_response_container = IResponseContainer(successor)
        predecessor_response_container = IResponseContainer(predecessor)

        self.assertEqual(0, len(successor_response_container))
        self.assertEqual(0, len(predecessor_response_container))

        with freeze(datetime(2016, 12, 9, 9, 40)):
            self.request['BODY'] = '{"text": "Completed!"}'
            endpoint = getMultiAdapter((predecessor, self.request),
                                       name="POST_application_json_@responses")
            endpoint.reply()

        self.assertEqual(1, len(successor_response_container))
        self.assertEqual(1, len(predecessor_response_container))


class TestTaskCreation(IntegrationTestCase):

    data = {
        "@type": "opengever.task.task",
        "title": "Bitte Dokument reviewen",
        "task_type": "direct-execution",
    }

    @browsing
    def test_with_responsible_containing_responsible_client(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible": {
                'token': "fa:{}".format(self.regular_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.secretariat_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            }
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        task, = children['added']
        self.assertEqual(self.regular_user.id, task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.secretariat_user.id, task.issuer)

    @browsing
    def test_with_responsible_containing_responsible_client_token_only(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible": "fa:{}".format(self.regular_user.id),
            "issuer": self.secretariat_user.id,
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        task, = children['added']
        self.assertEqual(self.regular_user.id, task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.secretariat_user.id, task.issuer)

    @browsing
    def test_without_responsible_client(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible_client": "fa",
            "responsible": {
                'token': self.regular_user.id,
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.secretariat_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            }
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))

        task, = children['added']
        self.assertEqual(self.regular_user.id, task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.secretariat_user.id, task.issuer)

    @browsing
    def test_without_responsible_client_token_only(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible": self.regular_user.id,
            "responsible_client": "fa",
            "issuer": self.secretariat_user.id,
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))

        task, = children['added']
        self.assertEqual(self.regular_user.id, task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.secretariat_user.id, task.issuer)

    @browsing
    def test_supports_inboxes(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible": "inbox:fa",
            "issuer": "inbox:fa",
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))

        task, = children['added']
        self.assertEqual('inbox:fa', task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual('inbox:fa', task.issuer)

    @browsing
    def test_supports_teams(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible": "team:1",
            "issuer": self.regular_user.id,
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))

        task, = children['added']
        self.assertEqual('team:1', task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.regular_user.id, task.issuer)

    @browsing
    def test_supports_responsible_from_hidden_orgunit(self, browser):
        self.login(self.regular_user, browser=browser)

        org_unit = get_current_org_unit()
        org_unit.hidden = True

        self.data.update({
            "responsible": "fa:{}".format(self.regular_user.id),
            "issuer": self.secretariat_user.id,
        })

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        task, = children['added']
        self.assertEqual(self.regular_user.id, task.responsible)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.secretariat_user.id, task.issuer)


class TestTaskPatch(IntegrationTestCase):

    @browsing
    def test_edit_responsible_with_responsible_client(self, browser):
        self.login(self.regular_user, browser=browser)

        self.add_additional_admin_and_org_unit()
        data = {
            "responsible": {
                'token': "rk:james.bond",
                'title': u'Ratskanzlei: James Bond'
            }
        }

        browser.open(self.task, json.dumps(data),
                     method="PATCH", headers=self.api_headers)

        self.assertEqual('rk', self.task.responsible_client)
        self.assertEqual('james.bond', self.task.responsible)
