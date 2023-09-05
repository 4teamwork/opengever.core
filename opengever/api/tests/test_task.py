from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.default_values import get_persisted_values_for_obj
from opengever.base.response import IResponseContainer
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.ogds.base.Extensions.plugins import activate_request_layer
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.ogds.base.utils import get_current_org_unit
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.restapi.serializer.converters import json_compatible
from zExceptions import BadRequest
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
import json


class TestTaskSerialization(SolrIntegrationTestCase):

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
             u'approved_documents': [],
             u'changes': [],
             u'created': json_compatible(self.subtask.created().utcdatetime()),
             u'creator': {u'title': u'Ziegler Robert', u'token': u'robert.ziegler'},
             u'mimetype': u'',
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
             u'related_items': [],
             u'rendered_text': u'',
             u'response_id': 1472652213000000,
             u'response_type': u'default',
             u'subtask': None,
             u'successor_oguid': u'',
             u'text': u'',
             u'transition': u'transition-add-subtask'},
            responses[0])

    @browsing
    def test_task_response_contains_changes(self, browser):
        # Modify deadline to have a response containing field changes
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.task)
        browser.click_on('Modify deadline')
        browser.fill({'Response': 'Nicht mehr dringend',
                      'New deadline': '1.1.2023'})
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
    def test_task_response_contains_subtask(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        api.content.transition(obj=self.subtask,
                               transition='task-transition-resolved-tested-and-closed')

        browser.open(self.task, method="GET", headers=self.api_headers)

        response = browser.json['responses'][-1]
        self.assertDictContainsSubset(
            {u'@id': self.subtask.absolute_url(),
             u'title': self.subtask.title},
            response['subtask'])

    @browsing
    def test_response_key_contains_empty_list_for_task_without_responses(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.inbox_task, method="GET", headers=self.api_headers)
        self.assertEquals([], browser.json['responses'])

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
             u'approved_documents': [],
             u'changes': [],
             u'creator': {
                 u'token': self.regular_user.id,
                 u'title': u'B\xe4rfuss K\xe4thi'},
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
             u'text': u'Angebot \xfcberpr\xfcft',
             u'transition': u'task-commented',
             u'subtask': None,
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
                u'dossier_type': None,
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
                u'dossier_type': None,
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
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
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
                    u'checked_out': u'',
                    u'description': u'',
                    u'file_extension': u'.docx',
                    u'is_leafnode': None,
                    u'review_state': u'document-state-draft',
                    u'title': u'Feedback zum Vertragsentwurf'
                }
            ],
            browser.json['items']
        )

    @browsing
    def test_sequence_type_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertEqual(None, browser.json['sequence_type'])

    @browsing
    def test_sequence_type_for_sequential_task(self, browser):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        self.login(self.regular_user, browser=browser)
        browser.open(self.sequential_task, method="GET", headers=self.api_headers)
        self.assertEqual({u'title': u'Sequenzieller Ablauf', u'token': u'sequential'},
                         browser.json['sequence_type'])

    @browsing
    def test_sequence_type_for_parallel_task(self, browser):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        self.login(self.regular_user, browser=browser)
        parallel_task = create(Builder('task')
                               .within(self.task)
                               .having(responsible_client='fa',
                                       responsible=self.regular_user.getId(),
                                       issuer=self.dossier_responsible.getId())
                               .as_parallel_task())
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertEqual({u'title': u'Paralleler Ablauf', u'token': u'parallel'},
                         browser.json['sequence_type'])

    @browsing
    def test_contains_creator(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertEqual(self.dossier_responsible.getId(),
                         browser.json['creator']['identifier'])

    @browsing
    def test_contains_is_remote_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertIn('is_remote_task', browser.json)
        self.assertFalse(browser.json['is_remote_task'])

    @browsing
    def test_contains_responsible_admin_unit_public_url(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertIn('responsible_admin_unit_url', browser.json)
        self.assertEqual('http://nohost/plone', browser.json['responsible_admin_unit_url'])

    @browsing
    def test_contains_has_remote_predecessor(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertIn('has_remote_predecessor', browser.json)
        self.assertFalse(browser.json['has_remote_predecessor'])

    @browsing
    def test_contains_is_completed(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)

        self.assertIn('is_completed', browser.json)
        self.assertFalse(browser.json['is_completed'])

        self.set_workflow_state('task-state-cancelled', self.task)
        browser.open(self.task, method="GET", headers=self.api_headers)

        self.assertTrue(browser.json['is_completed'])

    @browsing
    def test_contains_has_sequential_successor(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.seq_subtask_2, method="GET", headers=self.api_headers)
        self.assertTrue(browser.json['has_sequential_successor'])

        browser.open(self.seq_subtask_3, method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['has_sequential_successor'])

        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['has_sequential_successor'])

    @browsing
    def test_contains_is_current_user_responsible_flag(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertTrue(browser.json['is_current_user_responsible'])

        self.task.responsible = self.dossier_responsible.id
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['is_current_user_responsible'])

        # team: projekt_a
        self.task.responsible = 'team:1'
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertTrue(browser.json['is_current_user_responsible'])

        # inbox group
        self.task.responsible = 'inbox:fa'
        browser.open(self.task, method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['is_current_user_responsible'])


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


class TestTaskCreation(SolrIntegrationTestCase):

    data = {
        "@type": "opengever.task.task",
        "title": "Bitte Dokument reviewen",
        "task_type": "direct-execution",
    }

    @browsing
    def test_persists_default_value_for_deadline_when_passed(self, browser):
        self.login(self.regular_user, browser=browser)

        self.data.update({
            "responsible": {
                'token': "fa:{}".format(self.regular_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.secretariat_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            },
            "deadline": "2016-12-10"
        })

        with freeze(datetime(2016, 12, 5, 9, 40)), self.observe_children(self.dossier) as children:
            browser.open(self.dossier, json.dumps(self.data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        task, = children['added']

        persisted_values = get_persisted_values_for_obj(task)
        self.assertIn("deadline", persisted_values)
        self.assertEqual(persisted_values["deadline"], date(2016, 12, 10))

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
    def test_edit_responsible_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {"responsible": {'token': "fa:nicole.kohler"}}
        with browser.expect_http_error(400):
            browser.open(self.task, json.dumps(data),
                         method="PATCH", headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'It is not allowed to change the responsible here.'
                                    u' Use "Reassign" instead',
             u'message': u'change_responsible_not_allowed'}, browser.json)

    @browsing
    def test_changing_is_private_raise_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        # no change
        browser.open(self.task, json.dumps({"is_private": False}),
                     method="PATCH", headers=self.api_headers)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.task, json.dumps({"is_private": True}),
                         method="PATCH", headers=self.api_headers)

        self.assertEqual(
            "It's not allowed to change the is_private option of an existing task.",
            str(cm.exception))

    @browsing
    def test_changing_text_creates_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, headers=self.api_headers)
        responses = browser.json['responses']
        self.assertEquals(2, len(responses))

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Prefer': 'return=representation'}

        browser.open(self.task, json.dumps({"text": "New description"}),
                     method="PATCH", headers=headers)

        # Check that the responses are up to date in the serialized object
        # returned by the PATCH request.
        self.assertEqual(3, len(browser.json['responses']))
        self.assertEqual(
            [{u'after': u'New description',
              u'before': None,
              u'field_id': u'text',
              u'field_title': u''}],
            browser.json['responses'][-1]['changes'])

        browser.open(self.task, headers=self.api_headers)
        responses = browser.json['responses']
        self.assertEquals(3, len(responses))
        self.assertEquals(
            [{u'after': u'New description',
              u'before': None,
              u'field_id': u'text',
              u'field_title': u''}],
            responses[-1]['changes'])


class TestTaskTransitions(IntegrationTestCase):

    @browsing
    def test_reassign_task_with_combined_responsible_value(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assertEqual('fa', self.task.responsible_client)
        self.assertEqual('kathi.barfuss', self.task.responsible)

        data = {
            'responsible': {
                'token': 'rk:james.bond',
                'title': u'Ratskanzlei: James Bond'
            }
        }
        browser.open(self.task.absolute_url() + '/@workflow/task-transition-reassign',
                     json.dumps(data),
                     method="POST", headers=self.api_headers)

        self.assertEqual('rk', self.task.responsible_client)
        self.assertEqual('james.bond', self.task.responsible)
        self.assertEqual(['kathi.barfuss'], self.task.get_former_responsibles())

    @browsing
    def test_reassign_task_without_combined_responsible_value(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assertEqual('fa', self.task.responsible_client)
        self.assertEqual('kathi.barfuss', self.task.responsible)

        data = {
            'responsible': 'james.bond',
            'responsible_client': 'rk',
        }
        browser.open(self.task.absolute_url() + '/@workflow/task-transition-reassign',
                     json.dumps(data),
                     method="POST", headers=self.api_headers)

        self.assertEqual('rk', self.task.responsible_client)
        self.assertEqual('james.bond', self.task.responsible)

    @browsing
    def test_delegate_task(self, browser):
        self.login(self.regular_user, browser=browser)
        intids = getUtility(IIntIds)

        data = {
            "responsibles": ["fa:{}".format(self.regular_user.id),
                             "fa:{}".format(self.dossier_responsible.id)],
            "issuer": self.dossier_responsible.id,
            "title": "Delegated task",
            "deadline": "2019-11-30",
            "documents": [str(intids.getId(self.taskdocument))]
            }

        with self.observe_children(self.task) as children:
            browser.open(
                self.task.absolute_url() + '/@workflow/task-transition-delegate',
                json.dumps(data),
                method="POST",
                headers=self.api_headers)

        added_tasks = children['added']
        self.assertEqual(2, len(children['added']))
        self.assertItemsEqual(
            [self.regular_user.id, self.dossier_responsible.id],
            [task.responsible for task in added_tasks])

        for added_task in added_tasks:
            self.assertEqual(1, len(added_task.relatedItems))
            self.assertEqual(self.taskdocument, added_task.relatedItems[0].to_object)

        self.assertItemsEqual(['task-15', 'task-16'],
                              [task.id for task in added_tasks])

    @browsing
    def test_attachable_documents_vocabulary_lists_contained_and_related_documents(self, browser):
        intids = getUtility(IIntIds)
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task.absolute_url() + '/@vocabularies/opengever.task.attachable_documents_vocabulary',
            headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            [el.UID() for el in [self.document, self.taskdocument]],
            [term['token'] for term in browser.json['items']])


class TestAddingAdditionalTaskToSequentialProcessPost(IntegrationTestCase):

    @browsing
    def test_adds_task_to_the_given_position(self, browser):
        data = {
            "@type": "opengever.task.task",
            "title": "Subtask",
            "task_type": "direct-execution",
            "position": 1,
            "responsible": {
                'token': "fa:{}".format(self.secretariat_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.regular_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            }
        }

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.sequential_task) as subtasks:
            browser.open(self.sequential_task, json.dumps(data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(subtasks['added']))

        oguids = self.sequential_task.get_tasktemplate_order()
        self.assertEquals(
            [u'Mitarbeiter Dossier generieren',
             u'Subtask',
             u'Arbeitsplatz vorbereiten',
             u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [oguid.resolve_object().title for oguid in oguids])

    @browsing
    def test_added_task_is_part_of_sequence(self, browser):
        data = {
            "@type": "opengever.task.task",
            "title": "Subtask",
            "task_type": "direct-execution",
            "position": 1,
            "responsible": {
                'token': "fa:{}".format(self.secretariat_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.regular_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            }
        }

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.sequential_task) as subtasks:
            browser.open(self.sequential_task, json.dumps(data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(subtasks['added']))
        additional_task, = subtasks['added']

        self.assertTrue(IPartOfSequentialProcess.providedBy(additional_task))

        self.assertEquals(
            additional_task.get_sql_object(),
            self.seq_subtask_1.get_sql_object().tasktemplate_successor)

    @browsing
    def test_adds_task_to_the_end_if_no_position_is_given(self, browser):
        data = {
            "@type": "opengever.task.task",
            "title": "Subtask",
            "task_type": "direct-execution",
            "responsible": {
                'token': "fa:{}".format(self.secretariat_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.regular_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            }
        }

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.sequential_task) as subtasks:
            browser.open(self.sequential_task, json.dumps(data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(subtasks['added']))

        oguids = self.sequential_task.get_tasktemplate_order()
        self.assertEquals(
            [u'Mitarbeiter Dossier generieren',
             u'Arbeitsplatz vorbereiten',
             u'Vorstellungsrunde bei anderen Mitarbeitern',
             u'Subtask'],
            [oguid.resolve_object().title for oguid in oguids])

    @browsing
    def test_raise_error_if_position_is_not_an_int(self, browser):
        data = {
            "@type": "opengever.task.task",
            "title": "Subtask",
            "position": "not a number",
            "task_type": "direct-execution",
            "responsible": {
                'token': "fa:{}".format(self.secretariat_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
            "issuer": {
                'token': self.regular_user.id,
                'title': u'Finanzamt: J\xfcrgen K\xf6nig'
            }
        }

        self.login(self.regular_user, browser=browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.sequential_task, json.dumps(data),
                         method="POST", headers=self.api_headers)

        self.assertEqual("Could not parse `position` attribute", str(cm.exception))
