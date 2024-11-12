from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
import json


class TestRoleAssignmentReportsGet(IntegrationTestCase):
    maxDiff = None

    @browsing
    def test_get_role_assignment_reports(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@role-assignment-reports',
             u'items': [
                {u'@id': u'http://nohost/plone/@role-assignment-reports/report_1',
                 u'@type': u'virtual.report.roleassignmentreport',
                 u'modified': u'2016-08-31T20:01:33+00:00',
                 u'principal_type': u'user',
                 u'principal_label': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                 u'principal_id': self.regular_user.getId(),
                 u'report_id': u'report_1',
                 u'state': u'in progress'},
                {u'@id': u'http://nohost/plone/@role-assignment-reports/report_0',
                 u'@type': u'virtual.report.roleassignmentreport',
                 u'modified': u'2016-08-31T20:01:33+00:00',
                 u'principal_type': u'user',
                 u'principal_label': u'Fischer J\xfcrgen (jurgen.fischer)',
                 u'principal_id': self.archivist.getId(),
                 u'report_id': u'report_0',
                 u'state': u'ready'}],
             u'items_total': 2}, browser.json)

    @browsing
    def test_get_role_assignment_report(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_0',
                     method='GET', headers=self.api_headers)
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/@role-assignment-reports/report_0',
                u'@type': u'virtual.report.roleassignmentreport',
                u'items': [
                    {
                        u'@id': u'http://nohost/plone/ordnungssystem',
                        u'@type': u'opengever.repository.repositoryroot',
                        u'UID': u'createrepositorytree000000000001',
                        u'description': u'',
                        u'is_leafnode': None,
                        u'reference_number': u'Client1',
                        u'review_state': u'repositoryroot-state-active',
                        u'roles': [u'Contributor'],
                        u'title': u'Ordnungssystem',
                        u'url': u'http://nohost/plone/ordnungssystem'
                    },
                    {
                        u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4', # noqa
                        u'@type': u'opengever.dossier.businesscasedossier',
                        u'UID': u'createtreatydossiers000000000018',
                        u'description': u'',
                        u'dossier_type': None,
                        u'is_leafnode': None,
                        u'is_subdossier': True,
                        u'reference_number': u'Client1 1.1 / 1.1.1',
                        u'review_state': u'dossier-state-active',
                        u'roles': [u'Reader', u'Editor', u'Reviewer'],
                        u'title': u'Subsubdossier',
                        u'url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4' # noqa
                    },
                    {
                        u'@id': u'http://nohost/plone/ordnungssystem/rechnungsprufungskommission',
                        u'@type': u'opengever.repository.repositoryfolder',
                        u'UID': u'createrepositorytree000000000004',
                        u'description': u'',
                        u'is_leafnode': True,
                        u'reference_number': u'Client1 2',
                        u'review_state': u'repositoryfolder-state-active',
                        u'roles': [u'Contributor', u'Publisher'],
                        u'title': u'2. Rechnungspr\xfcfungskommission',
                        u'url': u'http://nohost/plone/ordnungssystem/rechnungsprufungskommission'
                    }
                ],
                u'items_total': 3,
                u'modified': u'2016-08-31T20:01:33+00:00',
                u'principal_id': u'archivist',
                u'principal_label': u'Fischer J\xfcrgen (jurgen.fischer)',
                u'principal_type': u'user',
                u'referenced_roles': [
                    {u'id': u'Reader', u'title': u'Read'},
                    {u'id': u'Contributor', u'title': u'Add dossiers'},
                    {u'id': u'Editor', u'title': u'Edit dossiers'},
                    {u'id': u'Reviewer', u'title': u'Resolve dossiers'},
                    {u'id': u'Publisher', u'title': u'Reactivate dossiers'},
                    {u'id': u'DossierManager', u'title': u'Manage dossiers'},
                    {u'id': u'TaskResponsible', u'title': u'Task responsible'},
                    {u'id': u'Role Manager', u'title': u'Role manager'}
                ],
                u'report_id': u'report_0',
                u'state': u'ready'}, browser.json)

    @browsing
    def test_get_role_assignment_report_with_invalid_report_id_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/bla',
                         method='GET', headers=self.api_headers)
        self.assertEqual(
            {"message": "Invalid report_id 'bla'",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_get_role_assignment_reports_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='GET', headers=self.api_headers)

        self.assertEqual(401, browser.status_code)


class TestRoleAssignmentReportsPost(IntegrationTestCase):

    @browsing
    def test_post_role_assignment_reports(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2020, 4, 18)):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps(
                             {"principal_id": {'token': self.meeting_user.getId()}}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'@type': u'virtual.report.roleassignmentreport',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': 'user',
                          u'principal_label': u'J\xe4ger Herbert (herbert.jager)',
                          u'principal_id': self.meeting_user.getId(),
                          u'report_id': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_with_group(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2020, 4, 18)):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"principal_id": {'token': 'projekt_a'}}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'@type': u'virtual.report.roleassignmentreport',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': u'group',
                          u'principal_label': u'Projekt A',
                          u'principal_id': u'projekt_a',
                          u'report_id': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_can_handle_group_prefix(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2020, 4, 18)):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"principal_id": {'token': 'group:projekt_a'}}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'@type': u'virtual.report.roleassignmentreport',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': u'group',
                          u'principal_label': u'Projekt A',
                          u'principal_id': u'projekt_a',
                          u'report_id': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_with_invalid_principal_id(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2020, 4, 18)):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"principal_id": 'chaosqueen'}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'@type': u'virtual.report.roleassignmentreport',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': u'unknown principal',
                          u'principal_label': u'Unknown ID (chaosqueen)',
                          u'principal_id': u'chaosqueen',
                          u'report_id': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_without_principal_id_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST', headers=self.api_headers)
        self.assertEqual(
            {"message": "Property 'principal_id' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_role_assignment_reports_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST', headers=self.api_headers,
                         data=json.dumps({"principal_id": self.regular_user.getId()}))

        self.assertEqual(401, browser.status_code)


class TestRoleAssignmentReportsDelete(IntegrationTestCase):

    @browsing
    def test_delete_role_assignment_report(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_0',
                     method='GET', headers=self.api_headers)
        browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_0',
                     method='DELETE', headers=self.api_headers)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_0',
                         method='GET', headers=self.api_headers)

        self.assertEqual(
            {"message": "Invalid report_id 'report_0'",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_delete_role_assignment_reports_without_principal_id_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='DELETE', headers=self.api_headers)
        self.assertEqual(
            {"message": "report_id is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_delete_role_assignment_report_with_invalid_report_id_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/bla',
                         method='DELETE', headers=self.api_headers)
        self.assertEqual(
            {"message": "Invalid report_id 'bla'",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_delete_role_assignment_reports_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_1',
                         method='DELETE', headers=self.api_headers)

        self.assertEqual(401, browser.status_code)
