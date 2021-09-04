from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase


class TestCustomPropertiesFieldsetForDocumentEditForm(IntegrationTestCase):

    @browsing
    def test_group_is_hidden_when_no_property_sheets_are_defined(self, browser):
        PropertySheetSchemaStorage().clear()

        self.login(self.regular_user, browser)
        browser.open(self.document, view="@@edit")

        self.assertEqual(
            ['Common', 'Classification'], browser.css('legend').text
        )

    @browsing
    def test_group_is_visible_when_property_sheets_are_defined(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view="@@edit")

        self.assertEqual(
            ['Common', 'Classification', 'Custom properties'],
            browser.css('legend').text,
        )

    @browsing
    def test_edit_form_prefills_static_default(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'choice', u'language', u'Language', u'', True, values=choices,
                default=u'fr'
            )
        )

        browser.open(self.document, view="@@edit")
        widget = browser.find('Language')
        self.assertEqual('fr', widget.value)


class TestCustomPropertiesFieldsetForDocumentAddForm(IntegrationTestCase):

    @browsing
    def test_group_is_hidden_when_no_property_sheets_are_defined(self, browser):
        PropertySheetSchemaStorage().clear()

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view="++add++opengever.document.document")

        self.assertEqual(
            ['Common', 'Classification'], browser.css('legend').text
        )

    @browsing
    def test_group_is_visible_when_property_sheets_are_defined(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view="++add++opengever.document.document")

        self.assertEqual(
            ['Common', 'Classification', 'Custom properties'],
            browser.css('legend').text,
        )

    @browsing
    def test_add_form_prefills_static_default(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'choice', u'language', u'Language', u'', True, values=choices,
                default=u'fr'
            )
        )

        browser.open(self.dossier, view="++add++opengever.document.document")
        widget = browser.find('Language')
        self.assertEqual('fr', widget.value)
