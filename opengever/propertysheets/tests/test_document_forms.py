from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.propertysheets.testing import dummy_default_factory_fr
from opengever.testing import IntegrationTestCase
from plone import api


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

    @browsing
    def test_edit_form_prefills_default_from_default_factory(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'choice', u'language', u'Language', u'', True, values=choices,
                default_factory=dottedname(dummy_default_factory_fr)
            )
        )

        browser.open(self.document, view="@@edit")
        widget = browser.find('Language')
        self.assertEqual('fr', widget.value)

    @browsing
    def test_edit_form_prefills_default_from_default_expression(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'choice', u'language', u'Language', u'', True, values=choices,
                default_expression="portal/language"
            )
        )

        browser.open(self.document, view="@@edit")
        widget = browser.find('Language')
        self.assertEqual('en', widget.value)

    @browsing
    def test_edit_form_prefills_default_from_default_from_member(self, browser):
        self.login(self.regular_user, browser)

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'textline', u'location', u'Location', u'', False,
                default_from_member={'property': 'location'}
            )
        )

        member = api.user.get_current()
        member.setProperties({'location': 'Bern'})

        browser.open(self.document, view="@@edit")
        widget = browser.find('Location')
        self.assertEqual('Bern', widget.value)


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

    @browsing
    def test_add_form_prefills_default_from_default_factory(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'choice', u'language', u'Language', u'', True, values=choices,
                default_factory=dottedname(dummy_default_factory_fr)
            )
        )

        browser.open(self.dossier, view="++add++opengever.document.document")
        widget = browser.find('Language')
        self.assertEqual('fr', widget.value)

    @browsing
    def test_add_form_prefills_default_from_default_expression(self, browser):
        self.login(self.regular_user, browser)

        choices = [u'de', u'fr', u'en']
        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'choice', u'language', u'Language', u'', True, values=choices,
                default_expression="portal/language"
            )
        )

        browser.open(self.dossier, view="++add++opengever.document.document")
        widget = browser.find('Language')
        self.assertEqual('en', widget.value)

    @browsing
    def test_add_form_prefills_default_from_default_from_member(self, browser):
        self.login(self.regular_user, browser)

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'textline', u'location', u'Location', u'', False,
                default_from_member={'property': 'location'}
            )
        )

        member = api.user.get_current()
        member.setProperties({'location': 'Bern'})

        browser.open(self.dossier, view="++add++opengever.document.document")
        widget = browser.find('Location')
        self.assertEqual('Bern', widget.value)
