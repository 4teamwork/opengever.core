from ftw.builder import Builder
from ftw.builder import create
from ooxml_docprops import read_properties
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.docprops import DocPropertyWriter
from opengever.dossier.docprops import TemporaryDocFile
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter


class TestHandlers(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestHandlers, self).setUp()
        self.setup_fullname(fullname='Peter')
        self.set_docproperty_export_enabled(True)

        self.dossier = create(Builder('dossier').titled(u'Dossier'))
        self.target_dossier = create(Builder('dossier').titled(u'Target'))

        self.doc_with_gever_properties = create(
            Builder('document')
            .within(self.dossier)
            .titled("Document with file")
            .with_asset_file('with_gever_properties.docx'))

    def tearDown(self):
        super(TestHandlers, self).tearDown()
        self.set_docproperty_export_enabled(False)

    def set_document_property_referencenumber(self):
        DocPropertyWriter(self.doc_with_gever_properties).write_properties(
            False, {'Dossier.ReferenceNumber': 'ClientXY / 42'})

    def test_document_checkout_updates_doc_properties(self):
        self.set_document_property_referencenumber()

        manager = getMultiAdapter(
            (self.doc_with_gever_properties, self.request),
            ICheckinCheckoutManager)
        manager.checkout()

        expected_doc_properties = [
            ('User.ID', TEST_USER_ID,),
            ('User.FullName', 'Peter',),
            ('Dossier.ReferenceNumber', 'Client1 / 1'),
            ('Dossier.Title', 'Dossier'),
            ('Document.ReferenceNumber', 'Client1 / 1 / 1'),
            ('Document.SequenceNumber', '1'),
        ]

        with TemporaryDocFile(self.doc_with_gever_properties.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)
        self.assert_doc_properties_updated_journal_entry_generated(
            self.doc_with_gever_properties)

    def test_document_checkin_updates_doc_properties(self):
        manager = getMultiAdapter(
            (self.doc_with_gever_properties, self.request),
            ICheckinCheckoutManager)
        manager.checkout()
        self.set_document_property_referencenumber()

        manager.checkin()

        expected_doc_properties = [
            ('User.ID', TEST_USER_ID,),
            ('User.FullName', 'Peter',),
            ('Dossier.ReferenceNumber', 'Client1 / 1'),
            ('Dossier.Title', 'Dossier'),
            ('Document.ReferenceNumber', 'Client1 / 1 / 1'),
            ('Document.SequenceNumber', '1'),
        ]

        with TemporaryDocFile(self.doc_with_gever_properties.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)
    def test_copying_documents_updates_doc_properties(self):
        api.content.copy(source=self.doc_with_gever_properties,
                         target=self.target_dossier)

        copied_doc = self.target_dossier.getFirstChild()

        expected_doc_properties = [
            ('User.ID', TEST_USER_ID,),
            ('User.FullName', 'Peter',),
            ('Dossier.ReferenceNumber', 'Client1 / 2'),
            ('Dossier.Title', 'Target'),
            ('Document.ReferenceNumber', 'Client1 / 2 / 2'),
            ('Document.SequenceNumber', '2'),
        ]

        with TemporaryDocFile(copied_doc.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)

    def test_moving_documents_updates_doc_properties(self):
        api.content.move(source=self.doc_with_gever_properties,
                         target=self.target_dossier)

        moved_doc = self.target_dossier.getFirstChild()

        expected_doc_properties = [
            ('User.ID', TEST_USER_ID,),
            ('User.FullName', 'Peter',),
            ('Dossier.ReferenceNumber', 'Client1 / 2'),
            ('Dossier.Title', 'Target'),
            ('Document.ReferenceNumber', 'Client1 / 2 / 1'),
            ('Document.SequenceNumber', '1'),
        ]

        with TemporaryDocFile(moved_doc.file) as tmpfile:
            properties = read_properties(tmpfile.path)
            self.assertItemsEqual(expected_doc_properties, properties)
