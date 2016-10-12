from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from ooxml_docprops import read_properties
from opengever.dossier.docprops import DocPropertyWriter
from opengever.dossier.docprops import TemporaryDocFile
from opengever.dossier.tests import EXPECTED_DOC_PROPERTIES
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.journal.handlers import DOC_PROPERTIES_UPDATED
from opengever.journal.tests.utils import get_journal_entry
from opengever.journal.tests.utils import get_journal_length
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestDocPropertyWriter(FunctionalTestCase):

    use_default_fixture = False
    maxDiff = None

    def setUp(self):
        super(TestDocPropertyWriter, self).setUp()

        user, org_unit, admin_unit = create(
            Builder('fixture')
            .with_all_unit_setup()
            .with_user(**OGDS_USER_ATTRIBUTES))

        self.set_docproperty_export_enabled(True)

        self.dossier = create(Builder('dossier').titled(u'My dossier'))

    @property
    def writer(self):
        return DocPropertyWriter(self.document)

    def tearDown(self):
        self.set_docproperty_export_enabled(False)
        super(TestDocPropertyWriter, self).tearDown()

    def test_with_file(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .with_asset_file('with_gever_properties.docx'))

        self.assertTrue(self.writer.has_file())
        self.document.file = None
        self.assertFalse(self.writer.has_file())

    def test_is_export_enabled(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .with_asset_file('with_gever_properties.docx'))

        self.assertTrue(self.writer.is_export_enabled())
        self.set_docproperty_export_enabled(False)
        self.assertFalse(self.writer.is_export_enabled())

    def test_is_supported_file(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .with_asset_file('with_gever_properties.docx'))

        self.assertTrue(self.writer.is_supported_file())
        self.document.file.contentType = 'text/foo'
        self.assertFalse(self.writer.is_supported_file())

    def test_document_with_gever_properties_is_updated_with_all_properties(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled("My Document")
            .having(document_date=datetime(2010, 1, 3),
                    document_author=TEST_USER_ID,
                    receipt_date=datetime(2010, 1, 3),
                    delivery_date=datetime(2010, 1, 3))
            .with_asset_file('with_gever_properties.docx'))

        self.writer.update_doc_properties(only_existing=True)

        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(EXPECTED_DOC_PROPERTIES.items(), properties)

    def test_overwrites_properties_of_wrong_type(self):
        frozen_date = datetime(2010, 1, 1)
        with freeze(frozen_date):
            self.document = create(
                Builder('document')
                .within(self.dossier)
                .titled("Document with prop of wrong type")
                .with_asset_file('with_property_of_wrong_type.docx'))

        with TemporaryDocFile(self.document.file) as tmpfile:
            self.assertIn(
                ('ogg.document.document_date', frozen_date,),
                list(read_properties(tmpfile.path)))

    def test_files_with_custom_properties_are_not_updated(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled("Document with custom props")
            .with_asset_file('with_custom_properties.docx'))

        expected_doc_properties = [('Test', 'Peter',)]

        writer = DocPropertyWriter(self.document)
        writer.update_doc_properties(only_existing=True)
        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)

        self.assertEqual(1, get_journal_length(self.document))
        entry = get_journal_entry(self.document)
        self.assertNotEqual(entry['action']['type'], DOC_PROPERTIES_UPDATED)

    def test_properties_can_be_added_to_file_without_properties(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled("My Document")
            .having(document_date=datetime(2010, 1, 3),
                    document_author=TEST_USER_ID,
                    receipt_date=datetime(2010, 1, 3),
                    delivery_date=datetime(2010, 1, 3))
            .with_asset_file('without_custom_properties.docx'))

        writer = DocPropertyWriter(self.document)
        writer.update_doc_properties(only_existing=False)
        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(EXPECTED_DOC_PROPERTIES.items(), properties)

    def test_writes_additional_recipient_property_providers(self):
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled("My Document")
            .having(document_date=datetime(2010, 1, 3),
                    document_author=TEST_USER_ID,
                    receipt_date=datetime(2010, 1, 3),
                    delivery_date=datetime(2010, 1, 3))
            .with_asset_file('without_custom_properties.docx'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller'))
        address = create(Builder('address')
                         .for_contact(peter)
                         .labeled(u'Home')
                         .having(street=u'Musterstrasse 283',
                                 zip_code=u'1234',
                                 city=u'Hinterkappelen',
                                 country=u'Schweiz'))

        writer = DocPropertyWriter(
            self.document, recipient_data=(peter, address))
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
            self.assertItemsEqual(
                EXPECTED_DOC_PROPERTIES.items() +
                additional_recipient_properties.items(),
                properties)
