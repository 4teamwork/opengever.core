from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zExceptions import Unauthorized
import transaction


class TestWorkspaceClient(FunctionalWorkspaceClientTestCase):

    def test_raises_an_error_if_using_the_client_with_disabled_feature(self):
        self.enable_feature(False)
        with self.assertRaises(WorkspaceClientFeatureNotEnabled):
            WorkspaceClient()

    def test_raises_an_error_if_the_workspace_url_is_not_configured(self):
        with self.env(TEAMRAUM_URL=''):
            with self.assertRaises(WorkspaceURLMissing):
                WorkspaceClient()

    def test_raises_an_error_if_user_lacks_neccesary_permissions(self):
        with self.workspace_client_env() as client:
            client.request.get('/').json()

            roles = set(api.user.get_roles())
            self.grant(roles.difference({'WorkspaceClientUser'}))
            with self.assertRaises(Unauthorized):
                client.request.get('/').json()

    def test_make_requests_to_the_configured_workspace(self):
        with self.workspace_client_env() as client:
            response = client.request.get('/').json()

        self.assertEqual(self.portal.absolute_url(), response.get('@id'))

    def test_get_an_object(self):
        with self.workspace_client_env() as client:
            response = client.get(self.workspace.absolute_url())

        self.assertEqual(self.workspace.absolute_url(), response.get('@id'))

    def test_search_for_objects(self):
        with self.workspace_client_env() as client:
            response = client.search(UID=[self.workspace.UID()])

        self.assertEqual(1, response.get('items_total'))
        self.assertEqual(self.workspace.absolute_url(),
                         response.get('items')[0].get('@id'))

    def test_create_workspace(self):
        with self.observe_children(self.workspace_root) as children:
            with self.workspace_client_env() as client:
                response = client.create_workspace(title=u"My new w\xf6rkspace")
                transaction.commit()

        self.assertEqual(u"My new w\xf6rkspace", response.get('title'))

        workspace = children['added'].pop()
        self.assertEqual(workspace.title, response.get('title'))
