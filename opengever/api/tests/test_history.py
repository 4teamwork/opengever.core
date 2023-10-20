from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.document.approvals import IApprovalList
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from plone import api
from plone.uuid.interfaces import IUUID
import json


class TestHistoryPatchEndpointForDocuments(IntegrationTestCase):

    @browsing
    def test_reverting_to_older_version(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)

        self.assertEqual('VERSION 1 DATA', self.document.file.data)

        browser.open(self.document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('VERSION 0 DATA', self.document.file.data)

    @browsing
    def test_reverting_to_older_version_of_private_document(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.private_document, 0)
        create_document_version(self.private_document, 1)

        self.assertEqual('VERSION 1 DATA', self.private_document.file.data)

        browser.open(self.private_document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('VERSION 0 DATA', self.private_document.file.data)

    @browsing
    def test_reverting_to_older_version_of_inbox_document(self, browser):
        self.login(self.secretariat_user, browser)

        create_document_version(self.inbox_document, 0)
        create_document_version(self.inbox_document, 1)

        self.assertEqual('VERSION 1 DATA', self.inbox_document.file.data)

        browser.open(self.inbox_document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('VERSION 0 DATA', self.inbox_document.file.data)

    @browsing
    def test_reverting_to_older_version_creates_new_version(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)

        repo_tool = api.portal.get_tool('portal_repository')
        self.assertEqual(2, len(repo_tool.getHistory(self.document)))
        self.assertEqual(1, self.document.version_id)

        browser.open(self.document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(3, len(repo_tool.getHistory(self.document)))
        self.assertEqual(2, self.document.version_id)

    @browsing
    def test_reverting_to_older_version_does_not_revert_metadata(self, browser):
        self.login(self.regular_user, browser)

        self.document.title = "Title version 0"
        create_document_version(self.document, 0)
        self.document.title = "Title version 1"
        create_document_version(self.document, 1)

        self.assertEqual('Title version 1', self.document.title)

        browser.open(self.document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual('Title version 1', self.document.title)

    @browsing
    def test_reverting_to_older_version_of_private_document_does_not_revert_metadata(self, browser):
        self.login(self.regular_user, browser)

        self.private_document.title = "Title version 0"
        create_document_version(self.private_document, 0)
        self.private_document.title = "Title version 1"
        create_document_version(self.private_document, 1)

        self.assertEqual('Title version 1', self.private_document.title)

        browser.open(self.private_document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual('Title version 1', self.private_document.title)

    @browsing
    def test_reverting_to_older_version_of_inbox_document_does_not_revert_metadata(self, browser):
        self.login(self.secretariat_user, browser)

        self.inbox_document.title = "Title version 0"
        create_document_version(self.inbox_document, 0)
        self.inbox_document.title = "Title version 1"
        create_document_version(self.inbox_document, 1)

        self.assertEqual('Title version 1', self.inbox_document.title)

        browser.open(self.inbox_document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual('Title version 1', self.inbox_document.title)

    @browsing
    def test_reverting_to_older_version_fails_when_document_checked_out(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)
        self.checkout_document(self.document)

        self.assertEqual('VERSION 1 DATA', self.document.file.data)

        with browser.expect_http_error(401):
            browser.open(self.document,
                         view='@history',
                         data=json.dumps({"version": 0}),
                         method='PATCH',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Unauthorized()', u'type': u'Unauthorized'},
            browser.json)
        self.assertEqual('VERSION 1 DATA', self.document.file.data)

    @browsing
    def test_reverting_inexistant_version_fails(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)

        self.assertEqual('VERSION 0 DATA', self.document.file.data)

        with browser.expect_http_error(500):
            browser.open(self.document,
                         view='@history',
                         data=json.dumps({"version": 3}),
                         method='PATCH',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message':
                u"Retrieving of '<Document at {}>' failed. Version '3' "
                u"does not exist. ".format(self.document.absolute_url_path()),
             u'type': u'ArchivistRetrieveError'}, browser.json)
        self.assertEqual('VERSION 0 DATA', self.document.file.data)


class TestHistoryGetEndpointForDocuments(IntegrationTestCase):

    @browsing
    def test_ensures_document_creator_as_creator_of_initial_version(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, 0)
        versioner = Versioner(self.document)

        self.assertEqual(self.document.Creator(), u'robert.ziegler')
        self.assertEqual(0, versioner.get_current_version_id())
        self.assertEqual(
            'kathi.barfuss',
            versioner.get_version_metadata(0)['sys_metadata']['principal'])

        browser.open(self.document,
                     view='@history',
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        version = browser.json[0]
        self.assertEqual(0, version[u'version'])
        self.assertEqual(u'robert.ziegler', version['actor']['id'])

    @browsing
    def test_returns_emtpy_list_for_reader(self, browser):
        with self.login(self.regular_user):
            RoleAssignmentManager(self.portal).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )
            RoleAssignmentManager(self.leaf_repofolder).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )

        self.login(self.reader_user, browser)
        browser.open(
            self.document,
            view='@history',
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual([], browser.json)


class TestVersionsGetEndpointForDocuments(IntegrationTestCase):

    @browsing
    def test_ensures_document_creator_as_creator_of_initial_version(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, 0)
        versioner = Versioner(self.document)

        self.assertEqual(self.document.Creator(), u'robert.ziegler')
        self.assertEqual(0, versioner.get_current_version_id())
        self.assertEqual(
            'kathi.barfuss',
            versioner.get_version_metadata(0)['sys_metadata']['principal'])

        browser.open(self.document,
                     view='@versions',
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        versions = browser.json["items"]
        self.assertEqual(1, len(versions))
        version = browser.json["items"][0]
        self.assertEqual(0, version[u'version'])
        self.assertEqual(u'robert.ziegler', version['actor']['identifier'])

    @browsing
    def test_endpoint_is_batched(self, browser):
        self.login(self.regular_user, browser)
        for i in range(5):
            create_document_version(self.document, i)

        browser.open(self.document,
                     view='@versions?b_size=3',
                     method='GET',
                     headers=self.api_headers)

        resp = browser.json
        self.assertEqual(5, resp[u'items_total'])
        self.assertEqual(3, len(resp["items"]))
        self.assertEqual(4, resp["items"][0]['version'])
        self.assertEqual(2, resp["items"][-1]['version'])
        self.assertIn('batching', resp)
        self.assertEqual(
            "{}/@versions?b_start=3&b_size=3".format(self.document.absolute_url()),
            resp['batching']['next'])

        browser.open(resp['batching']['next'],
                     method='GET',
                     headers=self.api_headers)
        self.assertEqual([1, 0],
                         [each['version'] for each in browser.json['items']])

    @browsing
    def test_returns_different_bumblebee_checksums_for_different_versions(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, 0)
        create_document_version(self.document, 1)

        browser.open(self.document,
                     view='@versions/0',
                     method='GET',
                     headers=self.api_headers)

        checksum_1 = browser.json['bumblebee_checksum']

        browser.open(self.document,
                     view='@versions/1',
                     method='GET',
                     headers=self.api_headers)

        checksum_2 = browser.json['bumblebee_checksum']
        self.assertNotEqual(checksum_1, checksum_2)

    @browsing
    def test_returns_initial_version_details_for_lazy_initial_version(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        self.assertFalse(versioner.has_initial_version())

        browser.open(self.document,
                     view='@versions/0',
                     method='GET',
                     headers=self.api_headers)

        resp = browser.json
        self.assertEqual(0, resp[u'current_version_id'])
        self.assertEqual(u'0', resp[u"version"])

    @browsing
    def test_returns_initial_version_even_when_it_does_not_exist_yet(self, browser):
        self.login(self.regular_user, browser)
        versioner = Versioner(self.document)
        self.assertFalse(versioner.has_initial_version())

        browser.open(self.document,
                     view='@versions',
                     method='GET',
                     headers=self.api_headers)

        resp = browser.json
        self.assertEqual(1, resp[u'items_total'])
        self.assertEqual(1, len(resp["items"]))

        expected_data = {
            u'@id': "{}/@versions/0".format(self.document.absolute_url()),
            u'actor': {u'@id': u'http://nohost/plone/@actors/dossier_responsible',
                       u'identifier': u'dossier_responsible'},
            u'comments': u'Initial version',
            u'may_revert': False,
            u'time': u'2016-08-31T16:07:33',
            u'version': 0,
            u'approvals': []}

        self.assertEqual(expected_data, resp["items"][0])

        versioner.create_initial_version()
        self.assertTrue(versioner.has_initial_version())
        browser.open(self.document,
                     view='@versions',
                     method='GET',
                     headers=self.api_headers)

        resp = browser.json
        self.assertEqual(1, resp[u'items_total'])
        self.assertEqual(1, len(resp["items"]))
        expected_data['may_revert'] = True
        self.assertEqual(expected_data, browser.json["items"][0])

    @browsing
    def test_reader_may_not_revert_to_older_version(self, browser):
        self.login(self.regular_user, browser)
        create_document_version(self.document, 0)

        browser.open(
            self.document,
            view='@versions',
            method='GET',
            headers=self.api_headers
        )
        resp = browser.json
        self.assertEqual(1, resp[u'items_total'])
        self.assertEqual(1, len(resp["items"]))
        self.assertTrue(resp['items'][0]['may_revert'])

        RoleAssignmentManager(self.portal).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
        )
        RoleAssignmentManager(self.leaf_repofolder).add_or_update_assignment(
            SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
        )

        self.login(self.reader_user, browser)
        browser.open(
            self.document,
            view='@versions',
            method='GET',
            headers=self.api_headers
        )
        resp = browser.json
        self.assertEqual(1, resp[u'items_total'])
        self.assertEqual(1, len(resp["items"]))
        self.assertFalse(resp['items'][0]['may_revert'])

    @browsing
    def test_includes_approval_information(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)
        create_document_version(self.document, 2)

        approvals = IApprovalList(self.document)
        approvals.add(
            1, self.subtask, self.regular_user.id, datetime(2021, 7, 2))
        approvals.add(
            2, self.task, self.administrator.id, datetime(2021, 8, 2))
        approvals.add(
            2, self.subtask, self.secretariat_user.id, datetime(2021, 8, 13))

        browser.open(self.document, view='@versions',
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            [2, 1, 0],
            [item.get('version') for item in browser.json['items']])

        expected = [
            [{u'approved': u'2021-08-02T00:00:00',
              u'approver': u'nicole.kohler',
              u'task': {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
                        u'@type': u'opengever.task.task',
                        u'description': u'',
                        u'is_leafnode': None,
                        u'review_state': u'task-state-in-progress',
                        u'title': u'Vertragsentwurf \xdcberpr\xfcfen'},
              u'version_id': 2},
             {u'approved': u'2021-08-13T00:00:00',
              u'approver': u'jurgen.konig',
              u'task': {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                        u'@type': u'opengever.task.task',
                        u'description': u'',
                        u'is_leafnode': None,
                        u'review_state': u'task-state-resolved',
                        u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'},
              u'version_id': 2}],
            [{u'approved': u'2021-07-02T00:00:00',
              u'approver': u'kathi.barfuss',
              u'task': {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                        u'@type': u'opengever.task.task',
                        u'description': u'',
                        u'is_leafnode': None,
                        u'review_state': u'task-state-resolved',
                        u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'},
              u'version_id': 1}],
            []]

        self.assertEqual(expected,
                         [item.get('approvals') for item in browser.json['items']])
