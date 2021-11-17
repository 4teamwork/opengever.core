from opengever.kub.client import KuBClient
from opengever.kub.interfaces import IKuBSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestKubClient(IntegrationTestCase):

    def setUp(self):
        super(TestKubClient, self).setUp()
        api.portal.set_registry_record('base_url', u'kub', IKuBSettings)
        api.portal.set_registry_record('service_token', u'secret', IKuBSettings)

    def test_sets_authorization_token(self):
        client = KuBClient()
        self.assertIn('Authorization', client.session.headers)
        self.assertEqual(u'Token secret', client.session.headers['Authorization'])

    def test_kub_api_url(self):
        client = KuBClient()
        self.assertEqual(u'kub/api/v1/', client.kub_api_url)
