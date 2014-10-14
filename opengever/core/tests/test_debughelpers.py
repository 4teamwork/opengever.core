from AccessControl.SecurityManagement import getSecurityManager
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.testing import FunctionalTestCase


class TestDebughelpers(FunctionalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def assert_current_user(self, user_name):
        sm = getSecurityManager()
        current_user = sm.getUser()
        self.assertEquals(user_name, current_user.getUserName())

    def test_setup_plone_sets_security_context_to_system_processes(self):
        self.assert_current_user('test-user')
        setup_plone(self.portal)
        self.assert_current_user('System Processes')

    def test_get_first_plone_site(self):
        app = self.portal.restrictedTraverse('/')
        plone = get_first_plone_site(app)
        self.assertEquals('plone', plone.id)
