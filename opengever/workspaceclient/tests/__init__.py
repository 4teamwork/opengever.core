from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.tokenauth.testing.builders import KeyPairBuilder  # noqa
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase
from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.interfaces import IWorkspaceClientSettings
from opengever.workspaceclient.session import SESSION_STORAGE
from plone import api
import os
import transaction


DEFAULT_MARKER = object()


class FunctionalWorkspaceClientTestCase(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(FunctionalWorkspaceClientTestCase, self).setUp()

        # Generate a service user
        self.service_user = api.user.create(email="service-user@example.com",
                                            username='service.user')

        self.grant('ServiceKeyUser', 'Impersonator',
                   user_id=self.service_user.getId())

        # Minimal GEVER setup
        self.repository_root = create(Builder('repository_root'))
        self.leaf_repofolder = create(Builder('repository').within(self.repository_root))
        self.dossier = create(Builder('dossier').within(self.leaf_repofolder))

        # Teamraum setup
        self.workspace_root = create(Builder('workspace_root')
                                     .having(id='workspaces'))
        self.grant('WorkspaceUser', on=self.workspace_root)

        self.workspace = create(Builder('workspace').within(self.workspace_root))
        self.grant('WorkspaceMember', on=self.workspace)

        # Reset the session store
        SESSION_STORAGE.sessions = None

        self.enable_feature()

    @contextmanager
    def env(self, **env):
        """Temporary set env variables.
        """
        original = os.environ.copy()
        os.environ.update(env)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(original)

    def enable_feature(self, enabled=True):
        api.portal.set_registry_record(
            'is_feature_enabled', enabled, IWorkspaceClientSettings)

    @contextmanager
    def workspace_client_env(self, url=DEFAULT_MARKER):
        url = self.portal.absolute_url() if url is DEFAULT_MARKER else url

        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(url))

        transaction.commit()

        with self.env(TEAMRAUM_URL=url):
            yield WorkspaceClient()
