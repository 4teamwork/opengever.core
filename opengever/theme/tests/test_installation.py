from Products.CMFCore.utils import getToolByName
from opengever.theme.tests import FunctionalTestCase


class TestInstallation(FunctionalTestCase):

    def test_generic_setup_profile_is_installed(self):
        portal_setup = getToolByName(self.layer['portal'], 'portal_setup')
        version = portal_setup.getLastVersionForProfile('opengever.theme:default')
        self.assertNotEquals('unknown', version)
