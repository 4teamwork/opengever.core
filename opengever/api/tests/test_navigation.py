from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase


class TestNavigation(IntegrationTestCase):

    @restapi
    def test_navigation_contains_respository(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(endpoint='@navigation')
        self.assertEqual(api_client.status_code, 200)
        self.assertIn(u'tree', api_client.contents)
        self.assertEqual(u'http://nohost/plone/ordnungssystem/@navigation', api_client.contents['@id'])

    @restapi
    def test_navigation_on_subcontext(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document, endpoint='@navigation')
        self.assertEqual(api_client.status_code, 200)
        self.assertIn(u'tree', api_client.contents)
        self.assertEqual(u'http://nohost/plone/ordnungssystem/@navigation', api_client.contents['@id'])

    @restapi
    def test_navigation_id_in_components(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document)
        self.assertEqual(api_client.status_code, 200)
        self.assertEqual(
            u'http://nohost/plone/ordnungssystem/@navigation',
            api_client.contents['@components']['navigation']['@id'],
        )
