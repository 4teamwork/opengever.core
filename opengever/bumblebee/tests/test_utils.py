from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.testing import FunctionalTestCase
from plone import api


class TestIsBumblebeeFeatureEnabled(FunctionalTestCase):

    def test_true_if_registry_entry_is_true(self):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IGeverBumblebeeSettings)

        self.assertTrue(is_bumblebee_feature_enabled())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IGeverBumblebeeSettings)

        self.assertFalse(is_bumblebee_feature_enabled())
