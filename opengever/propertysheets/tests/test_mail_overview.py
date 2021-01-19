from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase


class TestMailOverviewWithCustomProperties(IntegrationTestCase):

    @browsing
    def test_mail_overview_renders_correctly_when_custom_properties_are_set(
        self, browser
    ):
        self.login(self.manager)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )
        self.mail_eml.document_type = u"question"
        IDocumentCustomProperties(self.mail_eml).custom_properties = {
            u"IDocumentMetadata.document_type.question": {u"foo": u"qux"}
        }

        self.login(self.regular_user, browser)

        # smoke-test will result in error when data converter raises
        browser.open(self.mail_eml, view="tabbedview_view-overview")

        # double check we have rendered a good page
        self.assertEqual(
            u"Inquiry",
            browser.css(
                "#form-widgets-IDocumentMetadata-document_type"
            ).first.text,
        )
