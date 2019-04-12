from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
import json

api_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}


class TestWorkspace(IntegrationTestCase):

    @browsing
    def test_user_can_add_a_workspace(self, browser):
        self.login(self.workspace_admin, browser=browser)
        payload = {
            "@type": "opengever.workspace.workspace",
            "title": "My workspace",
        }
        browser.open(self.workspace_root.absolute_url(), method='POST',
                     headers=api_headers, data=json.dumps(payload))

        workspace = self.workspace_root.listFolderContents()[-1]
        self.assertEqual('My workspace', workspace.title)

    @browsing
    def test_workspace_creator_is_responsible_and_input_is_ignored(self, browser):
        self.login(self.workspace_admin, browser=browser)
        payload = {
            "@type": "opengever.workspace.workspace",
            "title": "My workspace",
            "responsible": self.regular_user.getId()
        }
        browser.open(self.workspace_root.absolute_url(), method='POST',
                     headers=api_headers, data=json.dumps(payload))

        workspace = self.workspace_root.listFolderContents()[-1]
        self.assertEqual(self.workspace_admin.getId(),
                         IDossier(workspace).responsible)

    @browsing
    def test_user_can_edit_workspace(self, browser):
        self.login(self.workspace_owner, browser=browser)
        payload = {
            "@type": "opengever.workspace.workspace",
            "title": "Your workspace",
        }
        browser.open(self.workspace.absolute_url(), method='PATCH',
                     headers=api_headers, data=json.dumps(payload))

        workspace = self.workspace_root.listFolderContents()[-1]
        self.assertEqual('Your workspace', workspace.title)

    @browsing
    def test_responsible_value_is_ignored_on_editform(self, browser):
        self.login(self.workspace_owner, browser=browser)

        self.assertEqual(self.workspace_owner.getId(),
                         IDossier(self.workspace).responsible)

        payload = {
            "@type": "opengever.workspace.workspace",
            "responsible": self.regular_user.getId()
        }
        browser.open(self.workspace.absolute_url(), method='PATCH',
                     headers=api_headers, data=json.dumps(payload))

        self.assertEqual(self.workspace_owner.getId(),
                         IDossier(self.workspace).responsible)
