from opengever.kub.client import KuBClient
from opengever.kub.interfaces import IKuBSettings
from opengever.testing import IntegrationTestCase
from plone import api


class KuBIntegrationTestCase(IntegrationTestCase):

    person_jean = "person:9af7d7cc-b948-423f-979f-587158c6bc65"
    person_julie = "person:0e623708-2d0d-436a-82c6-c1a9c27b65dc"
    org_ftw = "organization:30bab83d-300a-4886-97d4-ff592e88a56a"
    memb_jean_ftw = "membership:8345fcfe-2d67-4b75-af46-c25b2f387448"

    def setUp(self):
        super(KuBIntegrationTestCase, self).setUp()
        api.portal.set_registry_record(
            'base_url', u'http://localhost:8000', IKuBSettings)
        api.portal.set_registry_record('service_token', u'secret', IKuBSettings)
        self.client = KuBClient()

    def mock_get_by_id(self, mocker, _id):
        url = u'{}search?id={}'.format(self.client.kub_api_url, _id)
        mocker.get(url, json=KUB_RESPONSES[url])
        return url

    def mock_search(self, mocker, query_str):
        url = u'{}search?q={}'.format(self.client.kub_api_url, query_str)
        mocker.get(url, json=KUB_RESPONSES[url])
        return url


# These responses are taken from performing these exact requests against
# the database defined in "fixtures/gever-testing.json" in the KUB repository.
KUB_RESPONSES = {
    "http://localhost:8000/api/v1/search?q=Julie": [
        {
            "id": "0e623708-2d0d-436a-82c6-c1a9c27b65dc",
            "typedId": "person:0e623708-2d0d-436a-82c6-c1a9c27b65dc",
            "type": "person",
            "thirdPartyId": None,
            "text": "Dupont Julie",
            "created": "2021-11-15T12:31:36.571000+01:00",
            "modified": "2021-11-15T12:31:36.571000+01:00"
        }
    ],
    "http://localhost:8000/api/v1/search?q=4Teamwork": [
        {
            "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
            "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a",
            "type": "organization",
            "thirdPartyId": None,
            "text": "4Teamwork",
            "created": "2021-11-15T14:24:40.986000+01:00",
            "modified": "2021-11-15T14:24:40.986000+01:00"
        },
        {
            "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
            "typedId": "membership:8345fcfe-2d67-4b75-af46-c25b2f387448",
            "type": "membership",
            "thirdPartyId": None,
            "text": "Dupont Jean - 4Teamwork (CEO)",
            "created": "2021-11-15T14:25:12.517000+01:00",
            "modified": "2021-11-15T14:25:12.517000+01:00",
            "organization": "30bab83d-300a-4886-97d4-ff592e88a56a"
        }
    ],
    "http://localhost:8000/api/v1/search?id=person:9af7d7cc-b948-423f-979f-587158c6bc65": [
        {
            "id": "9af7d7cc-b948-423f-979f-587158c6bc65",
            "typedId": "person:9af7d7cc-b948-423f-979f-587158c6bc65",
            "type": "person",
            "thirdPartyId": None,
            "text": "Dupont Jean",
            "created": "2021-11-15T12:31:03.461000+01:00",
            "modified": "2021-11-15T12:31:03.461000+01:00"
        }
    ],
    "http://localhost:8000/api/v1/search?id=membership:8345fcfe-2d67-4b75-af46-c25b2f387448": [
        {
            "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
            "typedId": "membership:8345fcfe-2d67-4b75-af46-c25b2f387448",
            "type": "membership",
            "thirdPartyId": None,
            "text": "Dupont Jean - 4Teamwork (CEO)",
            "created": "2021-11-15T14:25:12.517000+01:00",
            "modified": "2021-11-15T14:25:12.517000+01:00",
            "organization": "30bab83d-300a-4886-97d4-ff592e88a56a"
        }
    ],
    "http://localhost:8000/api/v1/search?id=organization:30bab83d-300a-4886-97d4-ff592e88a56a": [
        {
            "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
            "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a",
            "type": "organization",
            "thirdPartyId": None,
            "text": "4Teamwork",
            "created": "2021-11-15T14:24:40.986000+01:00",
            "modified": "2021-11-15T14:24:40.986000+01:00"
        }
    ],
    "http://localhost:8000/api/v1/search?id=invalid-id": [],
}
