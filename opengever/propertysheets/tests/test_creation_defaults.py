from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.propertysheets.creation_defaults import get_customproperties_defaults
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def location_df(context):
    return u'CH'


mutable_default = {'a', 'b'}


@provider(IContextAwareDefaultFactory)
def mutable_default_df(context, default=mutable_default):
    return default


class TestPropertySheetsCreationDefaults(IntegrationTestCase):

    def test_dereferences_defaults_declared_as_mutable_kwargs(self):
        self.login(self.regular_user)
        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'multiple_choice', u'mutable',
                u'Field with mutable kwarg default', u'',
                required=True,
                values=('a', 'b', 'c'),
                default_factory=dottedname(mutable_default_df),
            )
        )

        field = IDocumentCustomProperties['custom_properties']
        defaults = get_customproperties_defaults(field)
        self.assertEqual(
            {'IDocument.default': {
                'mutable': set([u'a', u'b'])}},
            defaults)

        self.assertFalse(defaults['IDocument.default']['mutable'] is mutable_default)


class TestPropertySheetsCreationDefaultsForDocument(IntegrationTestCase):

    def test_doesnt_produce_empty_slots_if_no_defaults(self):
        self.login(self.regular_user)
        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'text', u'nodefault', u'Field without default', u'',
                required=False,
            )
        )

        field = IDocumentCustomProperties['custom_properties']
        defaults = get_customproperties_defaults(field)
        self.assertEqual({}, defaults)

    def test_determine_doc_defaults(self):
        self.login(self.regular_user)
        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'text', u'nodefault', u'Field without default', u'',
                required=False,
            )
            .with_field(
                'textline', u'notrequired', u'Optional field with default', u'',
                required=False,
                default=u'Not required, still has default'
            )
            .with_field(
                'multiple_choice', u'languages', u'Languages', u'',
                required=True, values=[u'de', u'fr', u'en'],
                default={u'de', u'en'},
            )
            .with_field(
                'choice', u'location', u'Location', u'',
                values=[u'CH', u'DE', u'US'],
                required=True,
                default_factory=dottedname(location_df),
            )
            .with_field(
                'textline', u'userid', u'User ID', u'',
                required=True,
                default_expression='member/getId',
            )
            .with_field(
                'textline', u'email', u'E-Mail', u'',
                required=True,
                default_from_member={'property': 'email'},
            )
            .with_field(
                'date', u'datefield', u'Date with default', u'',
                required=False,
                default=date(2022, 1, 31),
            )
        )

        field = IDocumentCustomProperties['custom_properties']
        defaults = get_customproperties_defaults(field)
        expected_defaults = {
            'IDocument.default': {
                'notrequired': u'Not required, still has default',
                'languages': {u'de', u'en'},
                'location': u'CH',
                'userid': self.regular_user.id,
                'email': u'foo@example.com',
                'datefield': date(2022, 1, 31),
            }
        }
        self.assertEqual(expected_defaults, defaults)


class TestPropertySheetsCreationDefaultsForDossier(IntegrationTestCase):

    def test_doesnt_produce_empty_slots_if_no_defaults(self):
        self.login(self.regular_user)
        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDossier.default')
            .with_field(
                'text', u'nodefault', u'Field without default', u'',
                required=False,
            )
        )

        field = IDossierCustomProperties['custom_properties']
        defaults = get_customproperties_defaults(field)
        self.assertEqual({}, defaults)

    def test_determine_dossier_defaults(self):
        self.login(self.regular_user)
        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDossier.default')
            .with_field(
                'text', u'nodefault', u'Field without default', u'',
                required=False,
            )
            .with_field(
                'textline', u'notrequired', u'Optional field with default', u'',
                required=False,
                default=u'Not required, still has default'
            )
            .with_field(
                'multiple_choice', u'languages', u'Languages', u'',
                required=True, values=[u'de', u'fr', u'en'],
                default={u'de', u'en'},
            )
            .with_field(
                'choice', u'location', u'Location', u'',
                values=[u'CH', u'DE', u'US'],
                required=True,
                default_factory=dottedname(location_df),
            )
            .with_field(
                'textline', u'userid', u'User ID', u'',
                required=True,
                default_expression='member/getId',
            )
            .with_field(
                'textline', u'email', u'E-Mail', u'',
                required=True,
                default_from_member={'property': 'email'},
            )
            .with_field(
                'date', u'datefield', u'Date with default', u'',
                required=False,
                default=date(2022, 1, 31),
            )
        )

        field = IDossierCustomProperties['custom_properties']
        defaults = get_customproperties_defaults(field)
        expected_defaults = {
            'IDossier.default': {
                'notrequired': u'Not required, still has default',
                'languages': {u'de', u'en'},
                'location': u'CH',
                'userid': self.regular_user.id,
                'email': u'foo@example.com',
                'datefield': date(2022, 1, 31),
            }
        }
        self.assertEqual(expected_defaults, defaults)
