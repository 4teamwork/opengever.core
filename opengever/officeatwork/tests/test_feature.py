from opengever.officeatwork import is_officeatwork_feature_enabled
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.testing import FunctionalTestCase
from plone import api


class TestIsOfficeatworkFeatureEnabled(FunctionalTestCase):

    def test_true_if_registry_entry_is_true(self):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IOfficeatworkSettings)

        self.assertTrue(is_officeatwork_feature_enabled())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IOfficeatworkSettings)

        self.assertFalse(is_officeatwork_feature_enabled())
