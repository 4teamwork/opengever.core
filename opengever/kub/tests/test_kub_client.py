from datetime import datetime
from ftw.testing import freeze
from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.testing import KuBIntegrationTestCase
import json
import pytz
import requests_mock


@requests_mock.Mocker()
class TestKubClient(KuBIntegrationTestCase):

    def test_sets_authorization_token(self, mocker):
        self.assertIn('Authorization', self.client.session.headers)
        self.assertEqual(u'Token secret', self.client.session.headers['Authorization'])

    def test_sets_accept_language_header(self, mocker):
        self.assertIn('Accept-Language', self.client.session.headers)
        self.assertEqual(u'en', self.client.session.headers['Accept-Language'])

    def test_kub_api_url(self, mocker):
        self.assertEqual(u'http://localhost:8000/api/v2/',
                         self.client.kub_api_url)

    def test_query_returns_persons(self, mocker):
        query_str = "Julie"
        url = self.mock_search(mocker, query_str)
        resp = self.client.query(query_str)
        results = resp.get('results')
        self.assertEqual(1, len(results))
        self.assertEqual("person", results[0]["type"])
        self.assertEqual(KUB_RESPONSES[url], resp)

    def test_query_returns_memberships_and_organizations(self, mocker):
        query_str = "4Teamwork"
        url = self.mock_search(mocker, query_str)
        resp = self.client.query(query_str)
        results = resp.get('results')
        self.assertEqual(2, len(results))
        self.assertEqual("organization", results[0]["type"])
        self.assertEqual("membership", results[1]["type"])
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

    def test_get_kub_id_label_mapping_uses_if_modified_since_header(self, mocker):
        labels = {'label_1': ' Maria Meier', 'label2': 'Donald Duck'}
        self.client._storage[self.client.STORAGE_MODIFIED_KEY] = 'Tue, 12 Oct 2021 13:37:00 GMT'
        self.client._storage[self.client.STORAGE_LABEL_MAPPING_KEY] = labels

        url = u'{}labels'.format(self.client.kub_api_url)
        mocker.get(url, status_code=304)
        self.assertEqual(labels, self.client.get_kub_id_label_mapping())
        self.assertEqual('Tue, 12 Oct 2021 13:37:00 GMT',
                         self.client._storage[self.client.STORAGE_MODIFIED_KEY])

        self.mock_labels(mocker)

        expected_labels = {
            u'person:9af7d7cc-b948-423f-979f-587158c6bc65': u'Dupont Jean',
            u'person:0e623708-2d0d-436a-82c6-c1a9c27b65dc': u'Dupont Julie',
            u'person:5db3e407-7fc3-4093-a6cf-96030044285a': u'Schaudi Julia',
            u'membership:8345fcfe-2d67-4b75-af46-c25b2f387448': u'Dupont Jean - 4Teamwork (CEO)',
            u'person:1193d423-ce13-4dd9-aa8d-1f224f6a2b96': u'Peter Hans',
            u'organization:30bab83d-300a-4886-97d4-ff592e88a56a': u'4Teamwork'}

        with freeze(datetime(2021, 10, 16, 12, 0, tzinfo=pytz.timezone('Europe/Zurich'))):
            self.assertEqual(expected_labels, self.client.get_kub_id_label_mapping())
            self.assertEqual('Tue, 12 Oct 2021 13:37:00 GMT',
                             mocker.last_request._request.headers['If-Modified-Since'])
            self.assertEqual('Sat, 16 Oct 2021 10:00:00 GMT',
                             self.client._storage[self.client.STORAGE_MODIFIED_KEY])

        with freeze(datetime(2021, 10, 19, 11, 35, tzinfo=pytz.timezone('Europe/Zurich'))):
            mocker.get(url, status_code=304)
            self.assertEqual(expected_labels, self.client.get_kub_id_label_mapping())
            self.assertEqual('Sat, 16 Oct 2021 10:00:00 GMT',
                             mocker.last_request._request.headers['If-Modified-Since'])
            self.assertEqual('Sat, 16 Oct 2021 10:00:00 GMT',
                             self.client._storage[self.client.STORAGE_MODIFIED_KEY])
