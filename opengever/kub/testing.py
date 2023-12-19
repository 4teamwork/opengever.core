# -*- coding: utf-8 -*-
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

    def mock_get_by_id(self, mocker, _id, **kwargs):
        url = self.client.get_resolve_url(_id)
        mocker.get(url, json=KUB_RESPONSES[url], **kwargs)
        return url

    def mock_search(self, mocker, query_str, **kwargs):
        url = u'{}search?q={}'.format(self.client.kub_api_url, query_str)
        mocker.get(url, json=KUB_RESPONSES[url], **kwargs)
        return url

    def mock_labels(self, mocker):
        url = u'{}labels'.format(self.client.kub_api_url)
        mocker.get(url, json=KUB_RESPONSES[url])
        return url


# These responses are taken from performing these exact requests against
# the database defined in "fixtures/gever-testing.json" in the KUB repository.
KUB_RESPONSES = {
    "http://localhost:8000/api/v2/search?q=Julie": {
        "results": [
            {
                "htmlUrl": "http://localhost:8000/people/0e623708-2d0d-436a-82c6-c1a9c27b65dc",
                "url": "http://localhost:8000/api/v2/people/0e623708-2d0d-436a-82c6-c1a9c27b65dc",
                "created": "2021-11-14T00:00:00+01:00",
                "id": "0e623708-2d0d-436a-82c6-c1a9c27b65dc",
                "organization": None,
                "modified": "2021-11-14T00:00:00+01:00",
                "text": "Dupont Julie",
                "thirdPartyId": None,
                "type": "person",
                "typedId": "person:0e623708-2d0d-436a-82c6-c1a9c27b65dc"
            }
        ]
    },

    "http://localhost:8000/api/v2/search?q=4Teamwork": {
        "results": [
            {
                "htmlUrl": "http://localhost:8000/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
                "url": "http://localhost:8000/api/v2/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
                "created": "2021-11-13T00:00:00+01:00",
                "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "organization": None,
                "modified": "2021-11-13T00:00:00+01:00",
                "text": "4Teamwork",
                "thirdPartyId": None,
                "type": "organization",
                "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a"
            },
            {
                "htmlUrl": None,
                "url": "http://localhost:8000/api/v2/memberships/8345fcfe-2d67-4b75-af46-c25b2f387448",
                "created": "2021-11-18T00:00:00+01:00",
                "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
                "organization": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "modified": "2021-11-18T00:00:00+01:00",
                "text": "Dupont Jean - 4Teamwork (CEO)",
                "thirdPartyId": None,
                "type": "membership",
                "typedId": "membership:8345fcfe-2d67-4b75-af46-c25b2f387448"
            }
        ]
    },

    "http://localhost:8000/api/v2/search?q=kohler&is_active=True": {
        "results": [
            {
                "htmlUrl": "http://localhost:8000/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
                "url": "http://localhost:8000/api/v2/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
                "created": "2021-11-13T00:00:00+01:00",
                "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "organization": None,
                "modified": "2021-11-13T00:00:00+01:00",
                "text": "Kohler KUB Active",
                "thirdPartyId": None,
                "type": "organization",
                "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a"
            },
        ]
    },

    "http://localhost:8000/api/v2/search?q=kohler": {
        "results": [
            {
                "htmlUrl": "http://localhost:8000/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
                "url": "http://localhost:8000/api/v2/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
                "created": "2021-11-13T00:00:00+01:00",
                "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "organization": None,
                "modified": "2021-11-13T00:00:00+01:00",
                "text": "Kohler KUB Active",
                "thirdPartyId": None,
                "type": "organization",
                "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a"
            },
            {
                "htmlUrl": None,
                "url": "http://localhost:8000/api/v2/memberships/8345fcfe-2d67-4b75-af46-c25b2f387448",
                "created": "2021-11-18T00:00:00+01:00",
                "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
                "organization": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "modified": "2021-11-18T00:00:00+01:00",
                "text": "Kohler KUB Inactive",
                "thirdPartyId": None,
                "type": "membership",
                "typedId": "membership:8345fcfe-2d67-4b75-af46-c25b2f387448"
            }
        ]
    },

    "http://localhost:8000/api/v2/resolve/person:9af7d7cc-b948-423f-979f-587158c6bc65": {
        "id": "9af7d7cc-b948-423f-979f-587158c6bc65",
        "personType": None,
        "personTypeTitle": None,
        "salutation": "Herr",
        "title": "",
        "firstName": "Jean",
        "officialName": "Dupont",
        "fullName": "Dupont Jean",
        "username": None,
        "dateOfBirth": "1992-05-15",
        "dateOfDeath": None,
        "readableAge": "30 Jahre und 6 Monate",
        "sex": None,
        "country": "",
        "countryIdISO2": "",
        "languageOfCorrespondance": "fr",
        "status": 1,
        "thirdPartyId": None,
        "description": "",
        "tags": [],
        "addresses": [
            {
                "id": "72b3120e-429f-423b-8bb7-31233d89026c",
                "label": "Home",
                "isDefault": True,
                "organisationName": "",
                "organisationNameAddOn1": "",
                "organisationNameAddOn2": "",
                "addressLine1": "",
                "addressLine2": "",
                "street": "Teststrasse",
                "houseNumber": "43",
                "dwellingNumber": "",
                "postOfficeBox": "",
                "swissZipCode": "9999",
                "swissZipCodeAddOn": "",
                "swissZipCodeId": "",
                "foreignZipCode": "",
                "locality": "",
                "town": "Bern",
                "countryIdISO2": "CH",
                "countryName": "Schweiz",
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            }
        ],
        "emailAddresses": [
            {
                "id": "3bc940de-ee8a-43b0-b373-3f1640122021",
                "label": "Private",
                "email": "Jean.dupon@example.com",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            }
        ],
        "phoneNumbers": [
            {
                "id": "e1046ad8-c4d7-4cac-93ac-d7c8298795e5",
                "label": "Mobile",
                "phoneNumber": "666 666 66 66",
                "phoneCategory": 2,
                "otherPhoneCategory": None,
                "phoneCategoryText": "Private Mobilnummer",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            {
                "id": "c62732e1-114e-4de7-a0b7-842c325bb068",
                "label": "Work",
                "phoneNumber": "999 999 99 99",
                "phoneCategory": 7,
                "otherPhoneCategory": None,
                "phoneCategoryText": u"Geschäftliche Mobilnummer",
                "isDefault": False,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            }
        ],
        "urls": [],
        "memberships": [
            {
                "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
                "organization": {
                    "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
                    "name": "4Teamwork",
                    "description": "Web application specialist",
                    "status": 1,
                    "thirdPartyId": None,
                    "memberCount": 1,
                    "modified": "2021-11-13T00:00:00+01:00",
                    "created": "2021-11-13T00:00:00+01:00"
                },
                "role": "CEO",
                "description": "",
                "department": "",
                "thirdPartyId": None,
                "start": "1990-02-24",
                "end": None,
                "primaryEmail": {
                    "id": "3bc940de-ee8a-43b0-b373-3f1640122021",
                    "label": "Private",
                    "email": "Jean.dupon@example.com",
                    "isDefault": True,
                    "thirdPartyId": None,
                    "modified": "2021-11-18T00:00:00+01:00",
                    "created": "2021-11-18T00:00:00+01:00"
                },
                "primaryAddress": {
                    "id": "ad0de780-3f62-400c-921a-0feb9e79c062",
                    "label": "Standort Bern",
                    "isDefault": True,
                    "organisationName": "",
                    "organisationNameAddOn1": "",
                    "organisationNameAddOn2": "",
                    "addressLine1": "c/o John Doe",
                    "addressLine2": "",
                    "street": "Dammweg",
                    "houseNumber": "9",
                    "dwellingNumber": "",
                    "postOfficeBox": "",
                    "swissZipCode": "3013",
                    "swissZipCodeAddOn": "",
                    "swissZipCodeId": "",
                    "foreignZipCode": "",
                    "locality": "",
                    "town": "Bern",
                    "countryIdISO2": "CH",
                    "countryName": "Schweiz",
                    "thirdPartyId": None,
                    "modified": "2021-11-18T00:00:00+01:00",
                    "created": "2021-11-18T00:00:00+01:00"
                },
                "primaryPhoneNumber": {
                    "id": "e1046ad8-c4d7-4cac-93ac-d7c8298795e5",
                    "label": "Mobile",
                    "phoneNumber": "666 666 66 66",
                    "phoneCategory": 2,
                    "otherPhoneCategory": None,
                    "phoneCategoryText": "Private Mobilnummer",
                    "isDefault": True,
                    "thirdPartyId": None,
                    "modified": "2021-11-18T00:00:00+01:00",
                    "created": "2021-11-18T00:00:00+01:00"
                }
            }
        ],
        "organizations": [
            {
                "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "name": "4Teamwork",
                "description": "Web application specialist",
                "status": 1,
                "thirdPartyId": None,
                "memberCount": 1,
                "modified": "2021-11-13T00:00:00+01:00",
                "created": "2021-11-13T00:00:00+01:00"
            }
        ],
        "primaryEmail": {
            "id": "3bc940de-ee8a-43b0-b373-3f1640122021",
            "label": "Private",
            "email": "Jean.dupon@example.com",
            "isDefault": True,
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "primaryPhoneNumber": {
            "id": "e1046ad8-c4d7-4cac-93ac-d7c8298795e5",
            "label": "Mobile",
            "phoneNumber": "666 666 66 66",
            "phoneCategory": 2,
            "otherPhoneCategory": None,
            "phoneCategoryText": "Private Mobilnummer",
            "isDefault": True,
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "modified": "2021-11-17T00:00:00+01:00",
        "created": "2021-11-17T00:00:00+01:00",
        "htmlUrl": "http://localhost:8000/people/9af7d7cc-b948-423f-979f-587158c6bc65",
        "url": "http://localhost:8000/api/v2/people/9af7d7cc-b948-423f-979f-587158c6bc65",
        "typedId": "person:9af7d7cc-b948-423f-979f-587158c6bc65",
        "type": "person",
        "primaryAddress": {
            "id": "72b3120e-429f-423b-8bb7-31233d89026c",
            "label": "Home",
            "isDefault": True,
            "organisationName": "",
            "organisationNameAddOn1": "",
            "organisationNameAddOn2": "",
            "addressLine1": "",
            "addressLine2": "",
            "street": "Teststrasse",
            "houseNumber": "43",
            "dwellingNumber": "",
            "postOfficeBox": "",
            "swissZipCode": "9999",
            "swissZipCodeAddOn": "",
            "swissZipCodeId": "",
            "foreignZipCode": "",
            "locality": "",
            "town": "Bern",
            "countryIdISO2": "CH",
            "countryName": "Schweiz",
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "primaryUrl": None,
        "text": "Dupont Jean",
        "customValues": {}
    },

    "http://localhost:8000/api/v2/resolve/membership:8345fcfe-2d67-4b75-af46-c25b2f387448": {
        "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
        "person": {
            "created": "2021-11-17T00:00:00+01:00",
            "firstName": "Jean",
            "fullName": "Dupont Jean",
            "htmlUrl": "http://localhost:8000/people/9af7d7cc-b948-423f-979f-587158c6bc65",
            "id": "9af7d7cc-b948-423f-979f-587158c6bc65",
            "isActive": True,
            "modified": "2021-11-17T00:00:00+01:00",
            "officialName": "Dupont",
            "personTypeTitle": None,
            "primaryEmail": {
                "id": "3bc940de-ee8a-43b0-b373-3f1640122021",
                "label": "Private",
                "email": "Jean.dupon@example.com",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            "salutation": "Herr",
            "tags": [],
            "thirdPartyId": None,
            "title": "",
            "url": "http://localhost:8000/api/v2/people/9af7d7cc-b948-423f-979f-587158c6bc65",
            "username": None,
            "countryDisplay": "-------",
            "dateOfBirth": "1992-05-15",
            "dateOfDeath": None,
            "description": "",
            "languageOfCorrespondanceDisplay": u"Französisch",
            "personType": None,
            "primaryAddress": {
                "id": "72b3120e-429f-423b-8bb7-31233d89026c",
                "label": "Home",
                "isDefault": True,
                "organisationName": "",
                "organisationNameAddOn1": "",
                "organisationNameAddOn2": "",
                "addressLine1": "",
                "addressLine2": "",
                "street": "Teststrasse",
                "houseNumber": "43",
                "dwellingNumber": "",
                "postOfficeBox": "",
                "swissZipCode": "9999",
                "swissZipCodeAddOn": "",
                "swissZipCodeId": "",
                "foreignZipCode": "",
                "locality": "",
                "town": "Bern",
                "countryIdISO2": "CH",
                "countryName": "Schweiz",
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            "primaryPhoneNumber": {
                "id": "e1046ad8-c4d7-4cac-93ac-d7c8298795e5",
                "label": "Mobile",
                "phoneNumber": "666 666 66 66",
                "phoneCategory": 2,
                "otherPhoneCategory": None,
                "phoneCategoryText": "Private Mobilnummer",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            "primaryUrl": None,
            "readableAge": "30 Jahre und 6 Monate",
            "sexDisplay": None,
            "statusDisplay": "Aktiv",
            "type": "person"
        },
        "organization": {
            "created": "2021-11-13T00:00:00+01:00",
            "description": "Web application specialist",
            "htmlUrl": "http://localhost:8000/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
            "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
            "isActive": True,
            "memberCount": 1,
            "modified": "2021-11-13T00:00:00+01:00",
            "name": "4Teamwork",
            "organizationTypeTitle": None,
            "primaryEmail": None,
            "spvCommittee": False,
            "status": 1,
            "thirdPartyId": None,
            "url": "http://localhost:8000/api/v2/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
            "organizationType": None,
            "primaryAddress": {
                "id": "ad0de780-3f62-400c-921a-0feb9e79c062",
                "label": "Standort Bern",
                "isDefault": True,
                "organisationName": "",
                "organisationNameAddOn1": "",
                "organisationNameAddOn2": "",
                "addressLine1": "c/o John Doe",
                "addressLine2": "",
                "street": "Dammweg",
                "houseNumber": "9",
                "dwellingNumber": "",
                "postOfficeBox": "",
                "swissZipCode": "3013",
                "swissZipCodeAddOn": "",
                "swissZipCodeId": "",
                "foreignZipCode": "",
                "locality": "",
                "town": "Bern",
                "countryIdISO2": "CH",
                "countryName": "Schweiz",
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            "primaryPhoneNumber": {
                "id": "4b92f284-4924-4608-8f6f-068c668ebdc8",
                "label": "Work",
                "phoneNumber": "111 111 11 11",
                "phoneCategory": 5,
                "otherPhoneCategory": None,
                "phoneCategoryText": u"Geschäftliche Nummer (Zentrale)",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            "primaryUrl": None,
            "statusDisplay": "Aktiv",
            "tags": [
                "Bude"
            ],
            "type": "organization"
        },
        "role": "CEO",
        "description": "",
        "department": "",
        "thirdPartyId": None,
        "start": "1990-02-24",
        "end": None,
        "typedId": "membership:8345fcfe-2d67-4b75-af46-c25b2f387448",
        "type": "membership",
        "url": "http://localhost:8000/api/v2/memberships/8345fcfe-2d67-4b75-af46-c25b2f387448",
        "text": "Dupont Jean - 4Teamwork (CEO)",
        "primaryEmail": {
            "id": "3bc940de-ee8a-43b0-b373-3f1640122021",
            "label": "Private",
            "email": "Jean.dupon@example.com",
            "isDefault": True,
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "primaryAddress": {
            "id": "ad0de780-3f62-400c-921a-0feb9e79c062",
            "label": "Standort Bern",
            "isDefault": True,
            "organisationName": "",
            "organisationNameAddOn1": "",
            "organisationNameAddOn2": "",
            "addressLine1": "c/o John Doe",
            "addressLine2": "",
            "street": "Dammweg",
            "houseNumber": "9",
            "dwellingNumber": "",
            "postOfficeBox": "",
            "swissZipCode": "3013",
            "swissZipCodeAddOn": "",
            "swissZipCodeId": "",
            "foreignZipCode": "",
            "locality": "",
            "town": "Bern",
            "countryIdISO2": "CH",
            "countryName": "Schweiz",
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "primaryPhoneNumber": {
            "id": "e1046ad8-c4d7-4cac-93ac-d7c8298795e5",
            "label": "Mobile",
            "phoneNumber": "666 666 66 66",
            "phoneCategory": 2,
            "otherPhoneCategory": None,
            "phoneCategoryText": "Private Mobilnummer",
            "isDefault": True,
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "primaryUrl": None
    },

    "http://localhost:8000/api/v2/resolve/organization:30bab83d-300a-4886-97d4-ff592e88a56a": {
        "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
        "organizationType": None,
        "organizationTypeTitle": None,
        "name": "4Teamwork",
        "description": "Web application specialist",
        "status": 1,
        "thirdPartyId": None,
        "memberCount": 1,
        "addresses": [
            {
                "id": "ad0de780-3f62-400c-921a-0feb9e79c062",
                "label": "Standort Bern",
                "isDefault": True,
                "organisationName": "",
                "organisationNameAddOn1": "",
                "organisationNameAddOn2": "",
                "addressLine1": "c/o John Doe",
                "addressLine2": "",
                "street": "Dammweg",
                "houseNumber": "9",
                "dwellingNumber": "",
                "postOfficeBox": "",
                "swissZipCode": "3013",
                "swissZipCodeAddOn": "",
                "swissZipCodeId": "",
                "foreignZipCode": "",
                "locality": "",
                "town": "Bern",
                "countryIdISO2": "CH",
                "countryName": "Schweiz",
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            },
            {
                "id": "602a873f-262f-4cc8-893b-41f5cb8e8b31",
                "label": "Standort St. Gallen",
                "isDefault": False,
                "organisationName": "",
                "organisationNameAddOn1": "",
                "organisationNameAddOn2": "",
                "addressLine1": "",
                "addressLine2": "",
                "street": "Oberer Graben",
                "houseNumber": "46",
                "dwellingNumber": "",
                "postOfficeBox": "",
                "swissZipCode": "9001",
                "swissZipCodeAddOn": "",
                "swissZipCodeId": "",
                "foreignZipCode": "",
                "locality": "",
                "town": "St. Gallen",
                "countryIdISO2": "CH",
                "countryName": "Schweiz",
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            }
        ],
        "emailAddresses": [],
        "phoneNumbers": [
            {
                "id": "4b92f284-4924-4608-8f6f-068c668ebdc8",
                "label": "Work",
                "phoneNumber": "111 111 11 11",
                "phoneCategory": 5,
                "otherPhoneCategory": None,
                "phoneCategoryText": u"Geschäftliche Nummer (Zentrale)",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2021-11-18T00:00:00+01:00",
                "created": "2021-11-18T00:00:00+01:00"
            }
        ],
        "urls": [],
        "memberships": [
            {
                "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
                "person": {
                    "created": "2021-11-17T00:00:00+01:00",
                    "description": "",
                    "firstName": "Jean",
                    "fullName": "Dupont Jean",
                    "htmlUrl": "http://localhost:8000/people/9af7d7cc-b948-423f-979f-587158c6bc65",
                    "id": "9af7d7cc-b948-423f-979f-587158c6bc65",
                    "modified": "2021-11-17T00:00:00+01:00",
                    "officialName": "Dupont",
                    "primaryEmail": {
                        "id": "3bc940de-ee8a-43b0-b373-3f1640122021",
                        "label": "Private",
                        "email": "Jean.dupon@example.com",
                        "isDefault": True,
                        "thirdPartyId": None,
                        "modified": "2021-11-18T00:00:00+01:00",
                        "created": "2021-11-18T00:00:00+01:00"
                    },
                    "status": 1,
                    "thirdPartyId": None,
                    "url": "http://localhost:8000/api/v2/people/9af7d7cc-b948-423f-979f-587158c6bc65",
                    "username": None
                },
                "role": "CEO",
                "description": "",
                "department": "",
                "thirdPartyId": None,
                "start": "1990-02-24",
                "end": None
            }
        ],
        "primaryEmail": None,
        "primaryPhoneNumber": {
            "id": "4b92f284-4924-4608-8f6f-068c668ebdc8",
            "label": "Work",
            "phoneNumber": "111 111 11 11",
            "phoneCategory": 5,
            "otherPhoneCategory": None,
            "phoneCategoryText": u"Geschäftliche Nummer (Zentrale)",
            "isDefault": True,
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "tags": [
            "Bude"
        ],
        "modified": "2021-11-13T00:00:00+01:00",
        "created": "2021-11-13T00:00:00+01:00",
        "htmlUrl": "http://localhost:8000/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
        "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a",
        "type": "organization",
        "url": "http://localhost:8000/api/v2/organizations/30bab83d-300a-4886-97d4-ff592e88a56a",
        "primaryAddress": {
            "id": "ad0de780-3f62-400c-921a-0feb9e79c062",
            "label": "Standort Bern",
            "isDefault": True,
            "organisationName": "",
            "organisationNameAddOn1": "",
            "organisationNameAddOn2": "",
            "addressLine1": "c/o John Doe",
            "addressLine2": "",
            "street": "Dammweg",
            "houseNumber": "9",
            "dwellingNumber": "",
            "postOfficeBox": "",
            "swissZipCode": "3013",
            "swissZipCodeAddOn": "",
            "swissZipCodeId": "",
            "foreignZipCode": "",
            "locality": "",
            "town": "Bern",
            "countryIdISO2": "CH",
            "countryName": "Schweiz",
            "thirdPartyId": None,
            "modified": "2021-11-18T00:00:00+01:00",
            "created": "2021-11-18T00:00:00+01:00"
        },
        "primaryUrl": None,
        "text": "4Teamwork",
        "spvCommittee": False,
        "customValues": {}
    },

    "http://localhost:8000/api/v2/resolve/invalid-id": ["Invalid uuid"],

    "http://localhost:8000/api/v2/resolve/person:0e623708-2d0d-436a-82c6-c1a9c27b65dc": {
        "id": "0e623708-2d0d-436a-82c6-c1a9c27b65dc",
        "personType": None,
        "personTypeTitle": None,
        "salutation": "Frau",
        "title": "",
        "firstName": "Julie",
        "officialName": "Dupont",
        "fullName": "Dupont Julie",
        "username": None,
        "dateOfBirth": None,
        "dateOfDeath": None,
        "readableAge": None,
        "sex": 2,
        "country": "",
        "countryIdISO2": "",
        "languageOfCorrespondance": "fr",
        "status": 1,
        "thirdPartyId": None,
        "description": "",
        "tags": [],
        "addresses": [],
        "emailAddresses": [],
        "phoneNumbers": [],
        "urls": [],
        "memberships": [],
        "organizations": [],
        "primaryEmail": None,
        "primaryPhoneNumber": None,
        "modified": "2021-11-14T00:00:00+01:00",
        "created": "2021-11-14T00:00:00+01:00",
        "htmlUrl": "http://localhost:8000/people/0e623708-2d0d-436a-82c6-c1a9c27b65dc",
        "url": "http://localhost:8000/api/v2/people/0e623708-2d0d-436a-82c6-c1a9c27b65dc",
        "typedId": "person:0e623708-2d0d-436a-82c6-c1a9c27b65dc",
        "type": "person",
        "primaryAddress": None,
        "primaryUrl": None,
        "text": "Dupont Julie",
        "customValues": {}
    },
    "http://localhost:8000/api/v2/labels": {
        "results": [
            {
                "id": "0e623708-2d0d-436a-82c6-c1a9c27b65dc",
                "typedId": "person:0e623708-2d0d-436a-82c6-c1a9c27b65dc",
                "label": "Dupont Julie"
            },
            {
                "id": "1193d423-ce13-4dd9-aa8d-1f224f6a2b96",
                "typedId": "person:1193d423-ce13-4dd9-aa8d-1f224f6a2b96",
                "label": "Peter Hans"
            },
            {
                "id": "5db3e407-7fc3-4093-a6cf-96030044285a",
                "typedId": "person:5db3e407-7fc3-4093-a6cf-96030044285a",
                "label": "Schaudi Julia"
            },
            {
                "id": "9af7d7cc-b948-423f-979f-587158c6bc65",
                "typedId": "person:9af7d7cc-b948-423f-979f-587158c6bc65",
                "label": "Dupont Jean"
            },
            {
                "id": "30bab83d-300a-4886-97d4-ff592e88a56a",
                "typedId": "organization:30bab83d-300a-4886-97d4-ff592e88a56a",
                "label": "4Teamwork"
            },
            {
                "id": "8345fcfe-2d67-4b75-af46-c25b2f387448",
                "typedId": "membership:8345fcfe-2d67-4b75-af46-c25b2f387448",
                "label": "Dupont Jean - 4Teamwork (CEO)"
            }
        ]
    }
}
