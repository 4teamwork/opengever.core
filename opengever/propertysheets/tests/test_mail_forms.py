from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestCustomPropertiesFieldsetForMailEditForm(IntegrationTestCase):

    @browsing
    def test_group_is_hidden_when_no_property_sheets_are_defined(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view="@@edit")

        self.assertEqual(
            ['Common', 'Classification'], browser.css('legend').text
        )

    @browsing
    def test_group_is_visible_when_property_sheets_are_defined(self, browser):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .with_field("text", u"foo", u"some input", u"", True)
        )

        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view="@@edit")

        self.assertEqual(
            ['Common', 'Classification', 'Custom properties'],
            browser.css('legend').text,
        )
