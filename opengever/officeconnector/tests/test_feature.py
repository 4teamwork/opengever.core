from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from plone import api


class TestIsOfficeConnectorFeatureEnabled(FunctionalTestCase):

    def test_registry_entry_defaults(self):
        self.assertTrue(is_officeconnector_attach_feature_enabled())
        self.assertTrue(is_officeconnector_checkout_feature_enabled())

    def test_if_registry_entries_are_true(self):
        api.portal.set_registry_record('attach_to_outlook_enabled', True,
                                       interface=IOfficeConnectorSettings)
        api.portal.set_registry_record('direct_checkout_and_edit_enabled', True,
                                       interface=IOfficeConnectorSettings)
        self.assertTrue(is_officeconnector_attach_feature_enabled())
        self.assertTrue(is_officeconnector_checkout_feature_enabled())

    def test_if_registry_entries_are_false(self):
        api.portal.set_registry_record('attach_to_outlook_enabled', False,
                                       interface=IOfficeConnectorSettings)
        api.portal.set_registry_record('direct_checkout_and_edit_enabled', False,
                                       interface=IOfficeConnectorSettings)
        self.assertFalse(is_officeconnector_attach_feature_enabled())
        self.assertFalse(is_officeconnector_checkout_feature_enabled())


class TestIsOfficeConnectorFeatureEnabledView(FunctionalTestCase):

    def test_registry_entry_defaults(self):
        self.assertTrue(self.portal.restrictedTraverse(
            '@@officeconnector_settings/is_attach_enabled')())
        self.assertTrue(self.portal.restrictedTraverse(
            '@@officeconnector_settings/is_checkout_enabled')())

    def test_if_registry_entry_is_true(self):
        api.portal.set_registry_record('attach_to_outlook_enabled', True,
                                       interface=IOfficeConnectorSettings)
        api.portal.set_registry_record('direct_checkout_and_edit_enabled', True,
                                       interface=IOfficeConnectorSettings)
        self.assertTrue(self.portal.restrictedTraverse(
            '@@officeconnector_settings/is_attach_enabled')())
        self.assertTrue(self.portal.restrictedTraverse(
            '@@officeconnector_settings/is_checkout_enabled')())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record('attach_to_outlook_enabled', False,
                                       interface=IOfficeConnectorSettings)
        api.portal.set_registry_record('direct_checkout_and_edit_enabled', False,
                                       interface=IOfficeConnectorSettings)
        self.assertFalse(self.portal.restrictedTraverse(
            '@@officeconnector_settings/is_attach_enabled')())
        self.assertFalse(self.portal.restrictedTraverse(
            '@@officeconnector_settings/is_checkout_enabled')())
