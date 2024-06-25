from datetime import datetime
from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from ftw.testing.freezer import freeze
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossiertransfer.tests.test_api_perform import KUB_LIST_EMPTY_RESP
from opengever.dossiertransfer.tests.test_api_perform import KUB_LIST_RESP
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.testing import IntegrationTestCase
import json
import requests_mock


class TestDossierSerializer(IntegrationTestCase):

    @browsing
    def test_dossiers_within_items_are_subdossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        business_case_dossiers = filter(
            lambda item: item.get("@type") == "opengever.dossier.businesscasedossier",
            browser.json["items"],
        )
        self.assertTrue(
            all([dossier["is_subdossier"] for dossier in business_case_dossiers]),
            'All dossiers within "self.dossier" must be subdossiers.'
        )

    @browsing
    def test_dossier_serializer_contains_blocked_local_roles(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertIn("blocked_local_roles", browser.json)

    @browsing
    def test_dossier_serializer_contains_is_after_resolved_jobs_pending(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertIn("has_pending_jobs", browser.json)

    @browsing
    def test_dossier_serializer_contains_is_protected(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertIn("is_protected", browser.json)

    @browsing
    def test_undeterminable_subdossier_within_items(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        business_case_dossiers = filter(
            lambda item: item.get("@type") != "opengever.dossier.businesscasedossier",
            browser.json["items"],
        )
        self.assertEqual(
            [],
            [
                dossier["is_subdossier"] for dossier in business_case_dossiers
                if dossier.get("is_subdossier", None) is not None
            ],
            'Non-dossiers within "self.dossier" cannot be subdossiers.'
        )

    @browsing
    def test_related_subdossier_is_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        dossier = create(Builder('dossier')
                         .within(self.leaf_repofolder)
                         .having(relatedDossier=[self.subdossier]))

        browser.open(dossier, method="GET", headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertTrue(
            browser.json["relatedDossier"][0]["is_subdossier"]
        )

    @browsing
    def test_related_branch_dossier_is_not_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        dossier = create(Builder('dossier')
                         .within(self.leaf_repofolder)
                         .having(relatedDossier=[self.empty_dossier]))

        browser.open(dossier, method="GET", headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertFalse(
            browser.json["relatedDossier"][0]["is_subdossier"]
        )

    @browsing
    def test_response_contains_dossier_touched_date(self, browser):
        self.login(self.regular_user, browser=browser)

        # The "touched" date is set correctly for newly created dossiers.
        with freeze(datetime(2020, 6, 12)):
            new_dossier = create(Builder("dossier")
                                 .within(self.branch_repofolder))
            browser.open(new_dossier, method="GET", headers=self.api_headers)
            self.assertEqual(u'2020-06-12', browser.json["touched"])

        # The dossier from the fixture must have been edited somewhere
        # because the "touched" date is not empty.
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertEqual(u"2016-08-31", browser.json["touched"])

    @browsing
    def test_contains_dossier_backreferences(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertEqual(
            [{u'description': u'',
              u'title': self.closed_meeting_dossier.title,
              u'is_subdossier': False, u'is_leafnode': None,
              u'dossier_type': None,
              u'review_state': u'dossier-state-active',
              u'@id': self.closed_meeting_dossier.absolute_url(),
              u'@type': u'opengever.meeting.meetingdossier',
              u'UID': u'createmeetings000000000000000007'}],
            browser.json['back_references_relatedDossier'])

        browser.open(self.subdossier, method="GET", headers=self.api_headers)
        self.assertEqual([], browser.json['back_references_relatedDossier'])

    @browsing
    def test_dossier_serializer_contains_filing_number(self, browser):
        self.activate_feature('filing_number')
        self.login(self.regular_user, browser=browser)
        IFilingNumber(self.dossier).filing_no = 'OG-Amt-2013-5'

        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertEqual('OG-Amt-2013-5', browser.json.get("filing_no"))


class TestMainDossierExpansion(IntegrationTestCase):

    @browsing
    def test_main_dossier_expansion_on_repository_root(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.repository_root.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertIsNone(
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_leaf_repofolder(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.leaf_repofolder.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertIsNone(
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_dossier(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.dossier.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createtreatydossiers000000000001',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_document(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.document.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createtreatydossiers000000000001',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createtreatydossiers000000000001',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.subdossier.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createtreatydossiers000000000001',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_subdocument(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.subdocument.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createtreatydossiers000000000001',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_subsubdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.subsubdossier.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createtreatydossiers000000000001',
                u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier '
                                u'abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'dossier_type': None,
                u'review_state': u'dossier-state-active',
                u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_dossiertemplate(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.dossiertemplate.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/vorlagen/dossiertemplate-1',
                u'@type': u'opengever.dossier.dossiertemplate',
                u'UID': u'createspecialtemplates0000000007',
                u'description': u'Lorem ipsum',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'review_state': None,
                u'title': u'Bauvorhaben klein',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_dossiertemplatedocument(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.dossiertemplatedocument.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/vorlagen/dossiertemplate-1',
                u'@type': u'opengever.dossier.dossiertemplate',
                u'UID': u'createspecialtemplates0000000007',
                u'description': u'Lorem ipsum',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'review_state': None,
                u'title': u'Bauvorhaben klein',
            },
            browser.json["@components"]['main-dossier'],
        )

    @browsing
    def test_main_dossier_expansion_on_subdossiertemplate(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.subdossiertemplate.absolute_url() + '?expand=main-dossier',
            method="GET",
            headers=self.api_headers,
        )
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/vorlagen/dossiertemplate-1',
                u'@type': u'opengever.dossier.dossiertemplate',
                u'UID': u'createspecialtemplates0000000007',
                u'description': u'Lorem ipsum',
                u'is_leafnode': None,
                u'is_subdossier': False,
                u'review_state': None,
                u'title': u'Bauvorhaben klein',
            },
            browser.json["@components"]['main-dossier'],
        )


class TestDossierDeserialization(IntegrationTestCase):

    loginname = 'dossier_responsible_loginame'

    @browsing
    def test_responsible_field_supports_loginname(self, browser):
        self.login(self.regular_user, browser)

        self.change_loginname(self.dossier_responsible.id, self.loginname)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Dossier A',
            u'responsible': self.loginname
        }

        response = browser.open(
            self.leaf_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            {u'token': self.dossier_responsible.id,
             u'title': u'Ziegler Robert (dossier_responsible_loginame)'},
            response.json.get('responsible'))

    @browsing
    def test_responsible_field_supports_userid(self, browser):
        self.login(self.regular_user, browser)

        self.change_loginname(self.dossier_responsible.id, self.loginname)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Dossier A',
            u'responsible': self.dossier_responsible.id
        }

        response = browser.open(
            self.leaf_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            {u'token': self.dossier_responsible.id,
             u'title': u'Ziegler Robert (dossier_responsible_loginame)'},
            response.json.get('responsible'))


@requests_mock.Mocker()
class TestDossierParticipationDeserializaton(KuBIntegrationTestCase):

    @browsing
    def test_adding_participations_of_existing_contacts(self, mocker, browser):
        self.login(self.regular_user, browser)

        self.mock_get_by_id(mocker, self.org_ftw)
        self.mock_get_by_id(mocker, self.person_jean)
        self.mock_labels(mocker)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Dossier A',
            u'responsible': self.dossier_responsible.id,
            u'participations': [
                {
                    'participant_id': self.org_ftw,
                    'roles': ['regard']},
                {
                    'participant_id': self.person_jean,
                    'roles': ['regard', 'participation']
                }
            ]
        }

        response = browser.open(
            self.leaf_repofolder.absolute_url(), data=json.dumps(payload),
            method='POST', headers=self.api_headers)

        self.assertEqual(response.status_code, 201)
        dossier = self.leaf_repofolder.get(browser.json['id'])
        browser.open(dossier, view='@participations', method='GET', headers=self.api_headers)

        expected = [{
            u'participant_actor': {
                u'identifier': u'organization:30bab83d-300a-4886-97d4-ff592e88a56a',
                u'@id': u'http://nohost/plone/@actors/organization:30bab83d-300a-4886-97d4-ff592e88a56a'},
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-21/@participations/organization:30bab83d-300a-4886-97d4-ff592e88a56a',
                u'participant_title': u'4Teamwork',
                u'roles': [u'regard'],
                u'participant_id': u'organization:30bab83d-300a-4886-97d4-ff592e88a56a'},
        {
            u'participant_actor': {
                u'identifier': u'person:9af7d7cc-b948-423f-979f-587158c6bc65',
                u'@id': u'http://nohost/plone/@actors/person:9af7d7cc-b948-423f-979f-587158c6bc65'},
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-21/@participations/person:9af7d7cc-b948-423f-979f-587158c6bc65',
                u'participant_title': u'Dupont Jean',
                u'roles': [u'regard', u'participation'],
                u'participant_id': u'person:9af7d7cc-b948-423f-979f-587158c6bc65'}]

        self.assertEqual(expected, browser.json['items'])

    @browsing
    def test_adding_participations_of_existing_contacts_by_thirdparty(self, mocker, browser):
        self.login(self.regular_user, browser)

        third_party_id = 'person:ea18df93-0fe7-4615-a859-cde16cc4dd23'

        self.mock_search_by_third_party_id(mocker, third_party_id=third_party_id, mocked_response=KUB_LIST_RESP)
        self.mock_labels(mocker)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Dossier A',
            u'responsible': self.dossier_responsible.id,
            u'participations': [
                {
                    'type': 'person',
                    'thirdPartyId': third_party_id,
                    'roles': ['regard']
                }
            ]
        }

        response = browser.open(
            self.leaf_repofolder.absolute_url(), data=json.dumps(payload),
            method='POST', headers=self.api_headers)

        self.assertEqual(response.status_code, 201)
        dossier = self.leaf_repofolder.get(browser.json['id'])
        browser.open(dossier, view='@participations', method='GET', headers=self.api_headers)

        self.assertEquals(1, len(browser.json['items']))
        self.assertEqual(u'person:20e024c9-db20-4ea1-999a-9deaa80413f4',
                         browser.json['items'][0]['participant_id'])
        self.assertEqual(['regard'], browser.json['items'][0]['roles'])

    @browsing
    def test_adding_participations_of_existing_contacts_by_name_and_date_of_birth(self, mocker, browser):
        self.login(self.regular_user, browser)

        url = '{}people?'.format(self.client.kub_api_url)
        mocker.get(url, json=KUB_LIST_EMPTY_RESP)

        self.mock_search_by_name_and_date_of_birth(
            mocker, firstname='Anna', official_name='Nass',
            date_of_birth='1992-05-15', mocked_response=KUB_LIST_RESP)
        self.mock_labels(mocker)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Dossier A',
            u'responsible': self.dossier_responsible.id,
            u'participations': [
                {
                    'type': 'person',
                    'firstName': 'Anna',
                    'officialName': 'Nass',
                    'dateOfBirth': '1992-05-15',
                    'roles': ['participation']
                }
            ]
        }

        response = browser.open(
            self.leaf_repofolder.absolute_url(), data=json.dumps(payload),
            method='POST', headers=self.api_headers)

        self.assertEqual(response.status_code, 201)
        dossier = self.leaf_repofolder.get(browser.json['id'])
        browser.open(dossier, view='@participations', method='GET', headers=self.api_headers)

        self.assertEquals(1, len(browser.json['items']))
        self.assertEqual(u'person:20e024c9-db20-4ea1-999a-9deaa80413f4',
                         browser.json['items'][0]['participant_id'])
        self.assertEqual(['participation'], browser.json['items'][0]['roles'])

    @browsing
    def test_adding_participation_with_new_contact(self, mocker, browser):
        self.login(self.regular_user, browser)

        # third_party_id
        url = '{}people?'.format(self.client.kub_api_url)
        mocker.get(url, json=KUB_LIST_EMPTY_RESP)

        # guessing
        self.mock_search_by_name_and_date_of_birth(
            mocker, firstname='Peter', official_name='Meier',
            date_of_birth='1992-05-15', mocked_response=KUB_LIST_EMPTY_RESP)
        self.mock_labels(mocker)

        # creation
        url = '{}people'.format(self.client.kub_api_url)
        mocker.post(url, json={'id': '9af7d7cc-b948-423f-979f-587158c6bc65'})

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Dossier A',
            u'responsible': self.dossier_responsible.id,
            u'participations': [
                {
                    'type': 'person',
                    'firstName': 'Jean',
                    'officialName': 'Dupont',
                    'dateOfBirth': '1992-05-15',
                    'roles': ['participation']
                }
            ]
        }

        response = browser.open(
            self.leaf_repofolder.absolute_url(), data=json.dumps(payload),
            method='POST', headers=self.api_headers)

        self.assertEqual(response.status_code, 201)
        dossier = self.leaf_repofolder.get(browser.json['id'])
        browser.open(dossier, view='@participations', method='GET', headers=self.api_headers)

        self.assertEquals(1, len(browser.json['items']))
        self.assertEqual(u'person:9af7d7cc-b948-423f-979f-587158c6bc65',
                         browser.json['items'][0]['participant_id'])
        self.assertEqual(u'Dupont Jean', browser.json['items'][0]['participant_title'])
        self.assertEqual(['participation'], browser.json['items'][0]['roles'])
