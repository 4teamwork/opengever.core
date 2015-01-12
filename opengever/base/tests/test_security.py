from AccessControl.SecurityManagement import SpecialUsers
from opengever.base.security import changed_security
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
