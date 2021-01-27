from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase


class TestDocumentDefaultViewWithCustomProperties(IntegrationTestCase):

    CUSTOM_PROPERTIES_LABEL = u"Custom properties"

    @browsing
    def test_document_default_view_displays_custom_properties(self, browser):
        self.login(self.manager)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )
        self.document.document_type = u"question"
        IDocumentCustomProperties(self.document).custom_properties = {
            u"IDocumentMetadata.document_type.question": {u"foo": u"qux"}
        }

        self.login(self.regular_user, browser)
        browser.open(self.document, view="view")

        table = browser.css(".dossier-detail-listing").first
        self.assertIsNotNone(table.find(self.CUSTOM_PROPERTIES_LABEL))
        data_row = table.lists()[-1]
        self.assertEqual(
            [self.CUSTOM_PROPERTIES_LABEL, "some input qux"], data_row
        )

    @browsing
    def test_document_default_view_displays_no_properties_label(self, browser):
        self.login(self.manager)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )
        self.document.document_type = u"contract"

        self.login(self.regular_user, browser)
        browser.open(self.document, view="view")

        table = browser.css(".dossier-detail-listing").first
        self.assertIsNotNone(table.find(self.CUSTOM_PROPERTIES_LABEL))
        data_row = table.lists()[-1]
        self.assertEqual(
            [
                self.CUSTOM_PROPERTIES_LABEL,
                "No custom properties are available.",
            ],
            data_row,
        )

    @browsing
    def test_document_default_view_hides_properties_when_no_sheet_is_defined(
        self, browser
    ):
        self.login(self.manager)

        self.login(self.regular_user, browser)
        browser.open(self.document, view="view")

        table = browser.css(".dossier-detail-listing").first
        self.assertIsNone(table.find(self.CUSTOM_PROPERTIES_LABEL))
