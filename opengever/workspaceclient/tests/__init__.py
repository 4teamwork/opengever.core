from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.tokenauth.testing.builders import KeyPairBuilder  # noqa
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase
from plone import api
import os


class FunctionalWorkspaceClientTestCase(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(FunctionalWorkspaceClientTestCase, self).setUp()

        # Minimal GEVER setup
        self.repo = create(Builder('repository_root'))

        # Generate a service user
        self.service_user = api.user.create(email="service-user@example.com",
                                            username='service.user')
        api.user.grant_roles(user=self.service_user,
                             roles=['ServiceKeyUser', 'Impersonator'])

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
