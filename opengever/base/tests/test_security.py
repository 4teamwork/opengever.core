from AccessControl.SecurityManagement import SpecialUsers
from opengever.base.security import changed_security
from opengever.base.security import elevated_privileges
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID


class TestSecurity(FunctionalTestCase):

    def setUp(self):
        super(TestSecurity, self).setUp()
        self.test_user = api.user.get(userid=TEST_USER_ID)

    def test_changed_security_sets_priviledged_user_and_restores_old(self):
        self.assertEqual(self.test_user, api.user.get_current())
        with changed_security():
            self.assertEqual(
                SpecialUsers.system.getUserName(),
                api.user.get_current().getUserName())
        self.assertEqual(self.test_user, api.user.get_current())

    def test_elevated_privileges_sets_priviledged_user_and_restores_old(self):
        self.assertEqual(self.test_user, api.user.get_current())
        self.assertNotIn('manage', api.user.get_current().getRoles())

        with elevated_privileges():
            current_user = api.user.get_current()
            self.assertEqual(self.test_user, current_user)
            self.assertIn('manage', current_user.getRoles())

        self.assertNotIn('manage', api.user.get_current().getRoles())
        self.assertEqual(self.test_user, api.user.get_current())
