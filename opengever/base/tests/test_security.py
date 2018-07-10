from opengever.base.security import elevated_privileges
from opengever.testing import IntegrationTestCase
from plone import api


class TestSecurity(IntegrationTestCase):

    def test_elevated_privileges_sets_priviledged_user_and_restores_old(self):
        self.login(self.regular_user)

        self.assertEqual('kathi.barfuss', api.user.get_current().getId())
        self.assertNotIn('manage', api.user.get_current().getRoles())

        with elevated_privileges():
            self.assertEqual('kathi.barfuss', api.user.get_current().getId())
            self.assertIn('manage', api.user.get_current().getRoles())

        self.assertNotIn('manage', api.user.get_current().getRoles())
        self.assertEqual('kathi.barfuss', api.user.get_current().getId())

    def test_elevated_privileges_allows_custom_user_id(self):
        self.login(self.regular_user)

        self.assertEqual('kathi.barfuss', api.user.get_current().getId())
        self.assertNotIn('manage', api.user.get_current().getRoles())

        with elevated_privileges(user_id='peter'):
            self.assertEqual('peter', api.user.get_current().getId())
            self.assertIn('manage', api.user.get_current().getRoles())

        self.assertNotIn('manage', api.user.get_current().getRoles())
        self.assertEqual('kathi.barfuss', api.user.get_current().getId())
