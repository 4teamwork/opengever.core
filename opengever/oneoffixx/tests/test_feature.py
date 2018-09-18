from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.testing import IntegrationTestCase


class TestIsOneoffixxFeatureEnabled(IntegrationTestCase):

    def test_true_if_registry_entry_is_true(self):
        self.activate_feature("officeconnector-checkout")
        self.activate_feature("oneoffixx")
        self.assertTrue(is_oneoffixx_feature_enabled())

    def test_false_if_registry_entry_is_false(self):
        self.activate_feature("officeconnector-checkout")
        self.assertFalse(is_oneoffixx_feature_enabled())

    def test_false_if_officeconnector_checkout_is_disabled(self):
        self.deactivate_feature("officeconnector-checkout")
        self.activate_feature("oneoffixx")
        self.assertFalse(is_oneoffixx_feature_enabled())


class TestIsOneoffixxFeatureEnabledView(IntegrationTestCase):

    def test_true_if_registry_entry_is_true(self):
        self.activate_feature("officeconnector-checkout")
        self.activate_feature("oneoffixx")
        feature_view = self.portal.restrictedTraverse('@@is_oneoffixx_feature_enabled')
        self.assertTrue(feature_view())

    def test_false_if_registry_entry_is_false(self):
        self.activate_feature("officeconnector-checkout")
        feature_view = self.portal.restrictedTraverse('@@is_oneoffixx_feature_enabled')
        self.assertFalse(feature_view())

    def test_false_if_officeconnector_checkout_is_disabled(self):
        self.deactivate_feature("officeconnector-checkout")
        self.activate_feature("oneoffixx")
        feature_view = self.portal.restrictedTraverse('@@is_oneoffixx_feature_enabled')
        self.assertFalse(feature_view())
