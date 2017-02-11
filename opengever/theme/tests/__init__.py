from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from opengever.theme.testing import GEVERTHEME_FUNCTIONAL_TESTING
from unittest2 import TestCase
import transaction


class FunctionalTestCase(TestCase):
    layer = GEVERTHEME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, roles)
        transaction.commit()
