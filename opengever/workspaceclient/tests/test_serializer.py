from ftw.testbrowser import browsing
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
import transaction


class TestSerializer(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_dossier_serializer_includes_workspaces(self, browser):
        with self.workspace_client_env():
            browser.login()
            response = browser.open(self.dossier, method='GET',
                                    headers={'Accept': 'application/json'}).json

            self.assertEqual([], response.get('workspaces'))

            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            transaction.commit()

            response = browser.open(self.dossier, method='GET',
                                    headers={'Accept': 'application/json'}).json

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in response.get('workspaces')])
