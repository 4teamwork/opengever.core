from datetime import datetime
from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from ftw.testing.freezer import freeze
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from plone import api
import json


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
