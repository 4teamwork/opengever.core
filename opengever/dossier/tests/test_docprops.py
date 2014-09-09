from ftw.builder import Builder
from ftw.builder import create
from ooxml_docprops import read_properties
from opengever.dossier.docprops import DocPropertyWriter
from opengever.dossier.docprops import TemporaryDocFile
from opengever.journal.handlers import DOC_PROPERTIES_UPDATED
from opengever.journal.tests.utils import get_journal_entry
from opengever.journal.tests.utils import get_journal_length
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestDocPropertyWriter(FunctionalTestCase):

    expected_user_properties = {
        'User.ID': TEST_USER_ID,
        'User.FullName': 'Peter',
    }
    expected_dossier_properties = {
        'Dossier.ReferenceNumber': 'Client1 / 1',
        'Dossier.Title': 'My dossier',
    }
    expected_document_properties = {
        'Document.ReferenceNumber': 'Client1 / 1 / 1',
        'Document.SequenceNumber': '1',
    }

    def setUp(self):
        super(TestDocPropertyWriter, self).setUp()
        self.grant('Manager')
        self.setup_fullname(fullname='Peter')
        self.set_docproperty_export_enabled(True)

        self.dossier = create(Builder('dossier').titled(u'My dossier'))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled("Document with props")
            .with_asset_file('with_gever_properties.docx'))

    @property
    def writer(self):
        return DocPropertyWriter(self.document)

    def tearDown(self):
        self.set_docproperty_export_enabled(False)
        super(TestDocPropertyWriter, self).tearDown()

    def test_with_file(self):
        self.assertTrue(self.writer.has_file())
        self.document.file = None
        self.assertFalse(self.writer.has_file())

    def test_is_export_enabled(self):
        self.assertTrue(self.writer.is_export_enabled())
        self.set_docproperty_export_enabled(False)
        self.assertFalse(self.writer.is_export_enabled())

    def test_is_supported_file(self):
        self.assertTrue(self.writer.is_supported_file())
        self.document.file.contentType = 'text/foo'
        self.assertFalse(self.writer.is_supported_file())

    def test_existing_doc_properties_are_updated(self):
        expected_doc_properties = [
            ('User.ID', TEST_USER_ID,),
            ('User.FullName', 'Peter',),
            ('Dossier.ReferenceNumber', 'Client1 / 1'),
            ('Dossier.Title', 'My dossier'),
            ('Document.ReferenceNumber', 'Client1 / 1 / 1'),
            ('Document.SequenceNumber', '1'),
        ]

        self.writer.update_doc_properties(only_existing=True)
        with TemporaryDocFile(self.document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)

    def test_files_with_custom_properties_are_not_updated(self):
        document = create(
            Builder('document')
            .within(self.dossier)
            .titled("Document with custom props")
            .with_asset_file('with_custom_properties.docx'))

        expected_doc_properties = [('Test', 'Peter',)]

        writer = DocPropertyWriter(document)
        writer.update_doc_properties(only_existing=True)
        with TemporaryDocFile(document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)

        self.assertEqual(1, get_journal_length(document))
        entry = get_journal_entry(document)
        self.assertNotEqual(entry['action']['type'], DOC_PROPERTIES_UPDATED)

    def test_properties_can_be_added_to_file_without_properties(self):
        document = create(
            Builder('document')
            .within(self.dossier)
            .titled("Document without props")
            .with_asset_file('without_custom_properties.docx'))

        expected_doc_properties = [
            ('User.ID', TEST_USER_ID,),
            ('User.FullName', 'Peter',),
            ('Dossier.ReferenceNumber', 'Client1 / 1'),
            ('Dossier.Title', 'My dossier'),
            ('Document.ReferenceNumber', 'Client1 / 1 / 2'),
            ('Document.SequenceNumber', '2'),
        ]

        writer = DocPropertyWriter(document)
        writer.update_doc_properties(only_existing=False)
        with TemporaryDocFile(document.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)
