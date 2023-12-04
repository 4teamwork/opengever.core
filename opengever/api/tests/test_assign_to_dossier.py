from datetime import date
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.inbox.yearfolder import get_current_yearfolder
from opengever.testing import IntegrationTestCase
from plone import api
from zExceptions import BadRequest
import json


class TestAssignToDossier(IntegrationTestCase):

    @browsing
    def test_assign_forwarding_to_dossier_creates_a_new_task_from_the_forwarding_attributes(self, browser):
        self.login(self.secretariat_user, browser=browser)

        forwarding = self.inbox_forwarding

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
            }))

        self.assertEqual(201, browser.status_code)
        task = browser.json

        self.assertEqual(forwarding.title, task.get('title'))
        self.assertEqual(
            '{}:{}'.format(forwarding.responsible_client, forwarding.responsible),
            task.get('responsible').get('token'),)

        self.assertEquals('inbox:fa', task.get('issuer').get('token'))

    @browsing
    def test_assign_forwarding_to_dossier_moves_the_forwarding_into_the_yearfolder(self, browser):
        self.login(self.secretariat_user, browser=browser)

        forwarding = self.inbox_forwarding

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
            }))

        self.assertEqual(201, browser.status_code)

        yearfolder = self.inbox.get(str(date.today().year))
        self.assertEquals(
            forwarding, yearfolder.get('forwarding-1'),
            'The forwarding was not correctly moved in to the actual yearfolder')

    @browsing
    def test_assign_forwarding_to_dossier_creates_the_task_within_the_given_dossier(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
            }))

        self.assertEqual(201, browser.status_code)
        task = browser.json

        self.assertEquals(self.dossier.absolute_url(), task.get('parent').get('@id'))

    @browsing
    def test_assign_forwarding_to_dossier_copies_all_documents_to_the_task(self, browser):
        self.login(self.secretariat_user, browser=browser)

        document = self.inbox_forwarding_document

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
            }))

        self.assertEqual(201, browser.status_code)
        task = browser.json

        self.assertEquals(document.title,
                          task.get('items')[0].get('title'),
                          'The forwarded document is not copied to the task')

    @browsing
    def test_can_pass_task_payload_to_directly_create_a_user_defined_task_while_assigning(self, browser):
        self.login(self.secretariat_user, browser=browser)

        task_payload = {
            "@type": "opengever.task.task",
            "title": u"Manual t\xf6sk",
            "task_type": "correction",
            "deadline": "2018-12-03",
            "is_private": False,
            'revoke_permissions': True,
            "responsible": self.regular_user.id,
            "issuer": self.secretariat_user.id,
            "responsible_client": "fa"}

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
                'task': task_payload
            }))

        self.assertEqual(201, browser.status_code)
        task = browser.json

        self.assertEqual(u"Manual t\xf6sk", task.get('title'))
        self.assertEqual('fa:%s' % self.regular_user.id, task.get('responsible').get('token'))

        self.assertEquals(self.secretariat_user.id, task.get('issuer').get('token'))
        self.assertEqual('2018-12-03', task.get('deadline'))

    @browsing
    def test_combined_values_for_responsible_is_possible(self, browser):
        self.login(self.secretariat_user, browser=browser)

        task_payload = {
            "@type": "opengever.task.task",
            "title": u"Manual t\xf6sk",
            "task_type": "correction",
            "deadline": "2018-12-03",
            "is_private": False,
            'revoke_permissions': True,
            "responsible": 'fa:{}'.format(self.regular_user.id),
            "issuer": self.secretariat_user.id}

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
                'task': task_payload
            }))

        self.assertEqual(201, browser.status_code)
        task = browser.json

        self.assertEqual('fa:%s' % self.regular_user.id, task.get('responsible').get('token'))

    @browsing
    def test_assign_to_dossier_validates_add_permission(self, browser):
        self.login(self.secretariat_user, browser=browser)

        self.dossier.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(api.user.get_current().getId(), ['Reader']))

        self.assertFalse(api.user.has_permission('opengever.task: Add task', obj=self.dossier))
        with browser.expect_http_error(401):
            browser.open(
                self.inbox_forwarding.absolute_url(),
                view='@assign-to-dossier',
                method='POST',
                headers=self.api_headers,
                data=json.dumps({
                    'target_uid': self.dossier.UID(),
                }))

    @browsing
    def test_assign_to_dossier_validates_addable_types(self, browser):
        self.login(self.secretariat_user, browser=browser)

        self.assertTrue(api.user.has_permission('opengever.task: Add task', obj=self.dossier))

        with browser.expect_http_error(401):
            browser.open(
                self.inbox_forwarding.absolute_url(),
                view='@assign-to-dossier',
                method='POST',
                headers=self.api_headers,
                data=json.dumps({
                    'target_uid': self.inactive_dossier.UID(),
                }))

    @browsing
    def test_assign_to_dossier_links_the_forwarding_with_the_task(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            data=json.dumps({'target_uid': self.dossier.UID()}),
            headers=self.api_headers)

        task = browser.json
        predecessor = Oguid.parse(task.get('predecessor')).resolve_object()

        yearfolder = get_current_yearfolder(context=self.inbox)
        forwarding = yearfolder.objectValues()[0]

        self.assertEqual(predecessor, forwarding)

    @browsing
    def test_raises_bad_request_when_target_uid_parameter_is_missing(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.inbox_forwarding.absolute_url(),
                view='@assign-to-dossier',
                method='POST',
                data=json.dumps({}),
                headers=self.api_headers)

        self.assertEqual('Required parameter "target_uid" is missing in body',
                         str(cm.exception))

    @browsing
    def test_raises_bad_request_when_target_uid_does_not_exist(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.inbox_forwarding.absolute_url(),
                view='@assign-to-dossier',
                method='POST',
                data=json.dumps({'target_uid': 'not-existing'}),
                headers=self.api_headers)

        self.assertEqual('target_uid: "not-existing" does not exist', str(cm.exception))

    @browsing
    def test_raises_bad_request_when_target_uid_is_not_a_dossier(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.inbox_forwarding.absolute_url(),
                view='@assign-to-dossier',
                method='POST',
                data=json.dumps({'target_uid': self.document.UID()}),
                headers=self.api_headers)

        self.assertEqual(
            'target_uid: "createtreatydossiers000000000002" is not a dossier',
            str(cm.exception))

    @browsing
    def test_raises_bad_request_when_task_schema_is_invalid(self, browser):
        self.login(self.secretariat_user, browser=browser)

        task_payload = {
            "@type": "opengever.task.task",
            "title": u"Manual t\xf6sk",
            "deadline": "2018-12-03",
            "is_private": False,
            'revoke_permissions': True,
            "responsible": self.regular_user.id,
            "issuer": self.secretariat_user.id,
            "responsible_client": "fa"}

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.inbox_forwarding.absolute_url(),
                view='@assign-to-dossier',
                method='POST',
                data=json.dumps({
                    'target_uid': self.dossier.UID(),
                    'task': task_payload
                }),
                headers=self.api_headers)

        self.assertEqual(
            'The task schema is invalid. Field: task_type, Message: Required input is missing.',
            str(cm.exception))
