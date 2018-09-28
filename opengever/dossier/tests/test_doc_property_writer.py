from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ooxml_docprops import read_properties
from opengever.dossier.docprops import DocPropertyWriter
from opengever.dossier.docprops import TemporaryDocFile
from opengever.dossier.tests import EXPECTED_DOC_PROPERTIES
from opengever.journal.handlers import DOC_PROPERTIES_UPDATED
from opengever.journal.tests.utils import get_journal_entry
from opengever.journal.tests.utils import get_journal_length
from opengever.testing import assets
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile


class TestDocPropertyWriterExportDisabled(IntegrationTestCase):

    def test_export_is_disabled_when_feature_is_not_enabled(self):
        self.login(self.regular_user)

        self.assertFalse(DocPropertyWriter(self.document).is_export_enabled())


class TestDocPropertyWriter(IntegrationTestCase):

    maxDiff = None

    features = ('doc-properties',)

    def test_export_is_enabled_when_feature_is_enabled(self):
        self.login(self.regular_user)

        self.assertTrue(DocPropertyWriter(self.document).is_export_enabled())

    def test_is_supported_file(self):
        self.login(self.regular_user)

        writer = DocPropertyWriter(self.document)

        self.assertTrue(writer.is_supported_file())

        self.document.file.contentType = 'text/foo'

        self.assertFalse(writer.is_supported_file())

    def test_has_file(self):
        self.login(self.dossier_responsible)
        self.assertTrue(DocPropertyWriter(self.document).has_file())
        self.assertFalse(DocPropertyWriter(self.empty_document).has_file())

    def test_document_with_gever_properties_is_updated_with_all_properties(
            self,
        ):
        self.login(self.regular_user)
        self.with_asset_file('with_gever_properties.docx')

        (
            DocPropertyWriter(self.document)
            .update_doc_properties(only_existing=True)
            )

        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(EXPECTED_DOC_PROPERTIES.items(), properties)

    def test_overwrites_properties_of_wrong_type(self):
        self.login(self.regular_user)
        self.with_asset_file('with_property_of_wrong_type.docx')

        (
            DocPropertyWriter(self.document)
            .update_doc_properties(only_existing=False)
            )

        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = dict(read_properties(tmpfile.path))
            self.assertEqual(
                datetime(2010, 1, 3),
                properties['ogg.document.document_date'],
                )

    def test_files_with_custom_properties_are_not_updated(self):
        self.login(self.regular_user)
        self.with_asset_file('with_custom_properties.docx')

        expected_doc_properties = [('Test', 'Peter',)]

        (
            DocPropertyWriter(self.document)
            .update_doc_properties(only_existing=True)
            )

        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)

        self.assertEqual(1, get_journal_length(self.document))

        entry = get_journal_entry(self.document)

        self.assertNotEqual(entry['action']['type'], DOC_PROPERTIES_UPDATED)

    def test_properties_can_be_added_to_file_without_properties(self):
        self.login(self.regular_user)
        self.with_asset_file('without_custom_properties.docx')

        (
            DocPropertyWriter(self.document)
            .update_doc_properties(only_existing=False)
            )

        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(EXPECTED_DOC_PROPERTIES.items(), properties)

    def test_writes_additional_recipient_property_providers(self):
        self.login(self.regular_user)
        self.with_asset_file('without_custom_properties.docx')

        peter = create(
            Builder('person')
            .having(
                firstname=u'Peter',
                lastname=u'M\xfcller',
                )
            )

        address = create(
            Builder('address')
            .for_contact(peter)
            .labeled(u'Home')
            .having(
                street=u'Musterstrasse 283',
                zip_code=u'1234',
                city=u'Hinterkappelen',
                country=u'Schweiz',
                )
            )

        writer = DocPropertyWriter(
            self.document,
            recipient_data=(peter, address),
            )

        writer.update_doc_properties(only_existing=False)

        additional_recipient_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
            'ogg.recipient.address.street': u'Musterstrasse 283',
            'ogg.recipient.address.zip_code': '1234',
            'ogg.recipient.address.city': 'Hinterkappelen',
            'ogg.recipient.address.country': 'Schweiz',
            }

        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertDictContainsSubset(
                additional_recipient_properties,
                dict(properties),
                )

    def with_asset_file(self, filename):
        self.document.file = NamedBlobFile(
            assets.load(filename), filename=unicode(filename))
