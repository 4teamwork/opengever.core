from opengever.ris import is_ris_feature_enabled
from opengever.ris.interfaces import IRisSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestRisConfiguration(IntegrationTestCase):

    def test_feature_is_disabled_by_default(self):
        self.assertFalse(is_ris_feature_enabled())

    def test_feature_is_enabled_when_base_url_is_configured(self):
        api.portal.set_registry_record('base_url', u'localhost', IRisSettings)
        self.assertTrue(is_ris_feature_enabled())
