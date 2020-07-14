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
                 u'modified': u'2016-08-31T20:01:33+00:00',
                 u'principal_type': u'user',
                 u'principalid': u'kathi.barfuss',
                 u'reportid': u'report_1',
                 u'state': u'in progress'},
                {u'@id': u'http://nohost/plone/@role-assignment-reports/report_0',
                 u'modified': u'2016-08-31T20:01:33+00:00',
                 u'principal_type': u'user',
                 u'principalid': u'jurgen.fischer',
                 u'reportid': u'report_0',
                 u'state': u'ready'}],
             u'items_total': 2}, browser.json)

    @browsing
    def test_get_role_assignment_report(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_0',
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@role-assignment-reports/report_0',
             u'items': [{u'UID': u'createrepositorytree000000000001',
                         u'roles': [u'Contributor'],
                         u'url': u'http://nohost/plone/ordnungssystem'},
                        {u'UID': u'createrepositorytree000000000004',
                         u'roles': [u'Contributor', u'Publisher'],
                         u'url': u'http://nohost/plone/ordnungssystem/rechnungsprufungskommission'},
                        {u'UID': u'createtreatydossiers000000000018',
                         u'roles': [u'Reader', u'Editor', u'Reviewer'],
                         u'url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-'
                                 u'vereinbarungen/dossier-1/dossier-2/dossier-4'}],
             u'items_total': 3,
             u'modified': u'2016-08-31T20:01:33+00:00',
             u'principal_type': u'user',
             u'principalid': u'jurgen.fischer',
             u'reportid': u'report_0',
             u'state': u'ready'}, browser.json)

    @browsing
    def test_get_role_assignment_report_with_invalid_reportid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/bla',
                         method='GET', headers=self.api_headers)
        self.assertEqual(
            {"message": "Invalid reportid 'bla'",
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
                         data=json.dumps({"principalid": self.meeting_user.getId()}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': 'user',
                          u'principalid': self.meeting_user.getId(),
                          u'reportid': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_with_group(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2020, 4, 18)):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"principalid": 'projekt_a'}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': u'group',
                          u'principalid': u'projekt_a',
                          u'reportid': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_with_invalid_principalid(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2020, 4, 18)):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"principalid": 'chaosqueen'}))

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({u'@id': u'http://nohost/plone/@role-assignment-reports/report_2',
                          u'items': [],
                          u'items_total': 0,
                          u'modified': u'2020-04-18T00:00:00+00:00',
                          u'principal_type': u'unknown principal',
                          u'principalid': u'chaosqueen',
                          u'reportid': u'report_2',
                          u'state': u'in progress'}, browser.json)

    @browsing
    def test_post_role_assignment_reports_without_principalid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST', headers=self.api_headers)
        self.assertEqual(
            {"message": "Property 'principalid' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_role_assignment_reports_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='POST', headers=self.api_headers,
                         data=json.dumps({"principalid": self.regular_user.getId()}))

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
            {"message": "Invalid reportid 'report_0'",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_delete_role_assignment_reports_without_principalid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports',
                         method='DELETE', headers=self.api_headers)
        self.assertEqual(
            {"message": "reportid is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_delete_role_assignment_report_with_invalid_reportid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/bla',
                         method='DELETE', headers=self.api_headers)
        self.assertEqual(
            {"message": "Invalid reportid 'bla'",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_delete_role_assignment_reports_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.portal.absolute_url() + '/@role-assignment-reports/report_1',
                         method='DELETE', headers=self.api_headers)

        self.assertEqual(401, browser.status_code)
