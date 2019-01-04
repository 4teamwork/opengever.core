from opengever.testing import FunctionalTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TeamraumThemeTestCase(FunctionalTestCase):

    def setUp(self):
        super(TeamraumThemeTestCase, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
