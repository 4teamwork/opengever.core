from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase


class TestMove(IntegrationTestCase):

    @restapi
    def test_regular_user_can_move_document(self, api_client):
        self.login(self.regular_user, api_client)
        doc_id = self.document.getId()
        api_client.open(self.subdossier, endpoint='@move', data={"source": self.document.absolute_url()})
        self.assertEqual(200, api_client.status_code)
        self.assertIn(doc_id, self.subdossier)
