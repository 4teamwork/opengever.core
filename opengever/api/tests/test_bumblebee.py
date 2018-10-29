from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase


class TestBumblebeeSession(IntegrationTestCase):

    @restapi
    def test_create_bumblebee_session(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.portal, endpoint='@preview-session', method='POST')
        self.assertEqual(api_client.status_code, 204)
        self.assertIn('bumblebee-local', api_client.cookies)
