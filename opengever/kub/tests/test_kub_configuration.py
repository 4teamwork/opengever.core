from opengever.kub import is_kub_feature_enabled
from opengever.kub.interfaces import IKuBSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestKubConfiguration(IntegrationTestCase):

    def test_url_serves_as_feature_flag(self):
        self.assertFalse(is_kub_feature_enabled())
        api.portal.set_registry_record('base_url', u'localhost', IKuBSettings)
        self.assertTrue(is_kub_feature_enabled())
