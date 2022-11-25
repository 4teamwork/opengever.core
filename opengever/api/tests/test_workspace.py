from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestWorkspaceSerializer(IntegrationTestCase):

    @browsing
    def test_workspace_serialization_contains_can_manage_participants(self, browser):
        self.login(self.workspace_member, browser)
        response = browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertFalse(response.get(u'can_manage_participants'))

        self.login(self.workspace_owner, browser)
        response = browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertTrue(response.get(u'can_manage_participants'))

    @browsing
    def test_workspace_serialization_contains_responsible(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertEquals(
            {u'token': u'gunther.frohlich',
             u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)'},
            browser.json['responsible'])

    @browsing
    def test_workspace_serialization_contains_videoconferencing_url(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertIn(
            u'videoconferencing_url', browser.json)
        self.assertIn(
            u'https://meet.jit.si/', browser.json['videoconferencing_url'])

    @browsing
    def test_workspace_serialization_contains_email(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'1018013300@example.org', browser.json[u'email'])

    @browsing
    def test_workspace_serialization_contains_can_access_members(self, browser):
        self.login(self.workspace_guest, browser)
        browser.open(self.workspace, headers=self.api_headers)
        self.assertTrue(browser.json['can_access_members'])

        with self.login(self.workspace_admin, browser):
            self.workspace.hide_members_for_guests = True

        browser.open(self.workspace, headers=self.api_headers)
        self.assertFalse(browser.json['can_access_members'])
