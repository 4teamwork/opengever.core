from ftw.testbrowser import browsing
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase


class TestCustomPropertiesFieldsetForMailEditForm(IntegrationTestCase):

    @browsing
    def test_group_is_hidden_when_no_property_sheets_are_defined(self, browser):
        PropertySheetSchemaStorage().clear()

        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view="@@edit")

        self.assertEqual(
            ['Common', 'Classification'], browser.css('legend').text
        )

    @browsing
    def test_group_is_visible_when_property_sheets_are_defined(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view="@@edit")

        self.assertEqual(
            ['Common', 'Classification', 'Custom properties'],
            browser.css('legend').text,
        )
