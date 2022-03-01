from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestExpandableReferenceNumberBase(IntegrationTestCase):

    maxDiff = None
    compact_json = None
    expanded_json = None

    def assert_compact_components_contain_reference_number(
        self, context, browser
    ):
        browser.open(context, headers=self.api_headers)
        self.assertIn(u"reference-number", browser.json["@components"])
        self.assertDictEqual(
            self.compact_json,
            browser.json["@components"]["reference-number"],
        )

    def assert_expanded_components_contain_reference_number(
        self, context, browser
    ):
        browser.open(
            context,
            view="?expand=reference-number",
            headers=self.api_headers,
        )
        self.assertIn(u"reference-number", browser.json["@components"])
        self.assertDictEqual(
            self.expanded_json,
            browser.json["@components"]["reference-number"],
        )

    def assert_reference_number_view_response(self, context, browser):
        browser.open(
            context,
            view="@reference-number",
            headers=self.api_headers,
        )
        self.assertDictEqual(
            self.expanded_json,
            browser.json,
        )


class TestPloneSiteExpandableReferenceNumber(
    TestExpandableReferenceNumberBase
):

    compact_json = {
        u"@id": u"http://nohost/plone/@reference-number",
    }
    expanded_json = {
        u"@id": u"http://nohost/plone/@reference-number",
        u"parts": {u"site": [u"Client1"]},
        u"reference_number": u"Client1",
        u"sortable_reference_number": u"client00000001",
    }

    @browsing
    def test_plone_site_unexpanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_compact_components_contain_reference_number(
            self.portal, browser
        )

    @browsing
    def test_plone_site_expanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_expanded_components_contain_reference_number(
            self.portal, browser
        )

    @browsing
    def test_plone_site_reference_number_view(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_reference_number_view_response(self.portal, browser)


class TestRepoRootExpandableReferenceNumber(TestExpandableReferenceNumberBase):

    compact_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/@reference-number",
    }
    expanded_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/@reference-number",
        u"parts": {u"repositoryroot": [u""], u"site": [u"Client1"]},
        u"reference_number": u"Client1",
        u"sortable_reference_number": u"client00000001",
    }

    @browsing
    def test_repo_root_unexpanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_compact_components_contain_reference_number(
            self.repository_root, browser
        )

    @browsing
    def test_repo_root_expanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_expanded_components_contain_reference_number(
            self.repository_root, browser
        )

    @browsing
    def test_repo_root_reference_number_view(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_reference_number_view_response(
            self.repository_root, browser
        )


class TestRepoFolderExpandableReferenceNumber(
    TestExpandableReferenceNumberBase
):

    compact_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/@reference-number",  # noqa
    }
    expanded_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/@reference-number",  # noqa
        u"parts": {
            u"repository": [u"1", u"1"],
            u"repositoryroot": [u""],
            u"site": [u"Client1"],
        },
        u"reference_number": u"Client1 1.1",
        u"sortable_reference_number": u"client00000001 00000001.00000001",
    }

    @browsing
    def test_repo_folder_unexpanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_compact_components_contain_reference_number(
            self.leaf_repofolder, browser
        )

    @browsing
    def test_repo_folder_expanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_expanded_components_contain_reference_number(
            self.leaf_repofolder, browser
        )

    @browsing
    def test_repo_folder_reference_number_view(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_reference_number_view_response(
            self.leaf_repofolder, browser
        )


class TestDossierExpandableReferenceNumber(TestExpandableReferenceNumberBase):

    compact_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/@reference-number",  # noqa
    }
    expanded_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/@reference-number",  # noqa
        u"parts": {
            u"dossier": [u"1"],
            u"repository": [u"1", u"1"],
            u"repositoryroot": [u""],
            u"site": [u"Client1"],
        },
        u"reference_number": u"Client1 1.1 / 1",
        u"sortable_reference_number": u"client00000001 00000001.00000001 / 00000001",  # noqa
    }

    @browsing
    def test_document_unexpanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_compact_components_contain_reference_number(
            self.dossier, browser
        )

    @browsing
    def test_document_expanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_expanded_components_contain_reference_number(
            self.dossier, browser
        )

    @browsing
    def test_document_reference_number_view(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_reference_number_view_response(self.dossier, browser)


class TestDocumentExpandableReferenceNumber(TestExpandableReferenceNumberBase):

    compact_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@reference-number",  # noqa
    }
    expanded_json = {
        u"@id": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@reference-number",  # noqa
        u"parts": {
            u"document": [u"14"],
            u"dossier": [u"1"],
            u"repository": [u"1", u"1"],
            u"repositoryroot": [u""],
            u"site": [u"Client1"],
        },
        u"reference_number": u"Client1 1.1 / 1 / 14",
        u"sortable_reference_number": u"client00000001 00000001.00000001 / 00000001 / 00000014",  # noqa
    }

    @browsing
    def test_document_unexpanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_compact_components_contain_reference_number(
            self.document, browser
        )

    @browsing
    def test_document_expanded_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_expanded_components_contain_reference_number(
            self.document, browser
        )

    @browsing
    def test_document_reference_number_view(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assert_reference_number_view_response(self.document, browser)
