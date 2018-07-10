from opengever.base.security import elevated_privileges
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID


class TestSecurity(FunctionalTestCase):

    def setUp(self):
        super(TestSecurity, self).setUp()
        self.test_user = api.user.get(userid=TEST_USER_ID)

    def test_elevated_privileges_sets_priviledged_user_and_restores_old(self):
        self.assertEqual(TEST_USER_ID, api.user.get_current().getId())
        self.assertNotIn('manage', api.user.get_current().getRoles())

        with elevated_privileges():
            self.assertEqual(TEST_USER_ID, api.user.get_current().getId())
            self.assertIn('manage', api.user.get_current().getRoles())

        self.assertNotIn('manage', api.user.get_current().getRoles())
        self.assertEqual(TEST_USER_ID, api.user.get_current().getId())
