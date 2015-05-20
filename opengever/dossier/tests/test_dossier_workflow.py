from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone import api
from zExceptions import Unauthorized


class TestDossierWorkflow(FunctionalTestCase):

    def test_deleting_dossier_is_only_allowed_for_managers(self):
        repository_root, repository = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(repository))

        acl_users = api.portal.get_tool('acl_users')
        valid_roles = list(acl_users.portal_role_manager.valid_roles())
        valid_roles.remove('Manager')
        self.grant(*valid_roles)

        with self.assertRaises(Unauthorized):
            api.content.delete(obj=dossier)
