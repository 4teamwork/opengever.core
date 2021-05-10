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

        self.assertDictContainsSubset({
            'responsible': {
                u'token': u'gunther.frohlich',
                u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)'
            },
            'responsible_fullname': u'Fr\xf6hlich G\xfcnther',
            },
            browser.json
        )

    @browsing
    def test_workspace_serialization_contains_videoconferencing_url(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertIn(
            u'videoconferencing_url', browser.json)
        self.assertIn(
            u'https://meet.jit.si/', browser.json['videoconferencing_url'])
