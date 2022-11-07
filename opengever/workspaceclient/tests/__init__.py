from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.tokenauth.testing.builders import KeyPairBuilder  # noqa
from opengever.core.testing import OPENGEVER_FUNCTIONAL_SOLR_ZSERVER_TESTING
from opengever.testing import SolrFunctionalTestCase
from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.interfaces import IWorkspaceClientSettings
from opengever.workspaceclient.session import SESSION_STORAGE
from plone import api
from zope.component import queryUtility
from zope.ramcache.interfaces.ram import IRAMCache
import os
import transaction


DEFAULT_MARKER = object()


class FunctionalWorkspaceClientTestCase(SolrFunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_SOLR_ZSERVER_TESTING

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
        self.dossier = create(Builder('dossier')
                              .titled(u'My dossier')
                              .within(self.leaf_repofolder))
        self.expired_dossier = create(Builder('dossier').within(
            self.leaf_repofolder).in_state('dossier-state-resolved'))

        # Teamraum setup
        self.workspace_root = create(Builder('workspace_root')
                                     .having(id='workspaces'))
        self.grant('WorkspacesUser', 'WorkspacesCreator', on=self.workspace_root)

        self.workspace = create(Builder('workspace')
                                .having(title=u'Ein Teamraum')
                                .within(self.workspace_root))
        self.grant('WorkspaceMember', on=self.workspace)

        # Grant necessary permissions to use the workspace client
        self.grant('WorkspaceClientUser', *api.user.get_roles())

        # Reset the session store
        SESSION_STORAGE.sessions = None

        self.enable_feature()
        self.invalidate_cache()

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
        transaction.commit()

    def enable_linking(self, enabled=True):
        api.portal.set_registry_record(
            'is_linking_enabled', enabled, IWorkspaceClientSettings)
        transaction.commit()

    @contextmanager
    def workspace_client_env(self, url=DEFAULT_MARKER):
        url = self.portal.absolute_url() if url is DEFAULT_MARKER else url

        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(url))

        transaction.commit()

        with self.env(TEAMRAUM_URL=url):
            yield WorkspaceClient()

    def invalidate_cache(self):
        util = queryUtility(IRAMCache)
        util.invalidateAll()
