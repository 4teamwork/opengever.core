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
            "responsible": self.regular_user.getId()
        }
        browser.open(self.workspace_root.absolute_url(), method='POST',
                     headers=api_headers, data=json.dumps(payload))

        workspace = self.workspace_root.listFolderContents()[-1]
        self.assertEqual('My workspace', workspace.title)
        self.assertEqual(self.regular_user.getId(),
                         IDossier(workspace).responsible)
