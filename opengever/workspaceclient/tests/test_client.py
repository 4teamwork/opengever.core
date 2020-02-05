from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase


class TestWorkspaceClient(FunctionalWorkspaceClientTestCase):

    def test_raises_an_error_if_using_the_client_with_disabled_feature(self):
        self.enable_feature(False)
        with self.assertRaises(WorkspaceClientFeatureNotEnabled):
            WorkspaceClient()

    def test_raises_an_error_if_the_workspace_url_is_not_configured(self):
        with self.env(TEAMRAUM_URL=''):
            with self.assertRaises(WorkspaceURLMissing):
                WorkspaceClient()

    def test_make_requests_to_the_configured_workspace(self):
        with self.workspace_client_env() as client:
            response = client.request.get('/').json()

        self.assertEqual(self.portal.absolute_url(), response.get('@id'))
