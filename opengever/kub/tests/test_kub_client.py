from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.testing import KuBIntegrationTestCase
import json
import requests_mock


@requests_mock.Mocker()
class TestKubClient(KuBIntegrationTestCase):

    def test_sets_authorization_token(self, mocker):
        self.assertIn('Authorization', self.client.session.headers)
        self.assertEqual(u'Token secret', self.client.session.headers['Authorization'])

    def test_kub_api_url(self, mocker):
        self.assertEqual(u'http://localhost:8000/api/v1/',
                         self.client.kub_api_url)

    def test_query_returns_persons(self, mocker):
        query_str = "Julie"
        url = self.mock_search(mocker, query_str)
        resp = self.client.query(query_str)
        self.assertEqual(1, len(resp))
        self.assertEqual("person", resp[0]["type"])
        self.assertEqual(KUB_RESPONSES[url], resp)

    def test_query_returns_memberships_and_organizations(self, mocker):
        query_str = "4Teamwork"
        url = self.mock_search(mocker, query_str)
        resp = self.client.query(query_str)
        self.assertEqual(2, len(resp))
        self.assertEqual("organization", resp[0]["type"])
        self.assertEqual("membership", resp[1]["type"])
        self.assertEqual(KUB_RESPONSES[url], resp)

    def test_get_by_id_handles_persons(self, mocker):
        url = self.mock_get_by_id(mocker, self.person_jean)
        resp = self.client.get_by_id(self.person_jean)
        self.assertEqual("person", resp["type"])
        self.assertEqual(json.loads(json.dumps(KUB_RESPONSES[url])), resp)

    def test_get_by_id_handles_organizations(self, mocker):
        url = self.mock_get_by_id(mocker, self.org_ftw)
        resp = self.client.get_by_id(self.org_ftw)
        self.assertEqual("organization", resp["type"])
        self.assertEqual(KUB_RESPONSES[url], resp)

    def test_get_by_id_handles_memberships(self, mocker):
        url = self.mock_get_by_id(mocker, self.memb_jean_ftw)
        resp = self.client.get_by_id(self.memb_jean_ftw)
        self.assertEqual("membership", resp["type"])
        self.assertEqual(KUB_RESPONSES[url], resp)
