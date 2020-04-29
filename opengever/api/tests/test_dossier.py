from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


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
                if dossier["is_subdossier"] is not None
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
