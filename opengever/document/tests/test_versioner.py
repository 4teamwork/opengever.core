from datetime import datetime
from ftw.testbrowser import browsing
from opengever.document.docprops import DocPropertyWriter
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile
from zope.filerepresentation.interfaces import IRawWriteFile


class TestInitialVersionCreation(IntegrationTestCase):

    def test_initial_version_is_not_created_when_adding_a_document(self):
        self.login(self.regular_user)
        versioner = Versioner(self.document)

        self.assertFalse(versioner.has_initial_version())

    def test_initial_version_is_created_when_updating_the_file(self):
        self.login(self.regular_user)
        versioner = Versioner(self.document)

        self.assertFalse(versioner.has_initial_version())
        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')
        self.assertTrue(versioner.has_initial_version())
        self.assertEquals(
            1, versioner.get_history_metadata().getLength(countPurged=False))

    def test_doc_property_writer_creates_initial_version(self):
        self.activate_feature('doc-properties')
        self.login(self.dossier_responsible)

        versioner = Versioner(self.document)
        self.assertFalse(versioner.has_initial_version())

        DocPropertyWriter(self.document).update_doc_properties(only_existing=False)

        self.assertTrue(versioner.has_initial_version())
        self.assertEquals(
            1, versioner.get_history_metadata().getLength(countPurged=False))

    @browsing
    def test_initial_version_date_is_documents_creation_date(self, browser):
        self.login(self.manager)
        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')

        versioner = Versioner(self.document)
        version = versioner.repository.retrieve(self.document, 0)

        creation_date = self.document.creation_date
        creation_date = creation_date.asdatetime().replace(tzinfo=None)
        self.assertEquals(
            creation_date,
            datetime.fromtimestamp(version.sys_metadata.get('timestamp')))

    @browsing
    def test_initial_version_principal_is_documents_original_creator(self, browser):
        self.login(self.regular_user)

        # Guard assertion to make sure creatore of the fixture-document is
        # what we expect it to be.
        self.assertEqual('robert.ziegler', self.document.Creator())

        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')

        versioner = Versioner(self.document)
        versioner.create_version(comment='')

        initial_version_md = versioner.get_version_metadata(0)
        first_version_md = versioner.get_version_metadata(1)

        self.assertEqual(
            'robert.ziegler',
            initial_version_md['sys_metadata']['principal'])

        self.assertEqual(
            'kathi.barfuss',
            first_version_md['sys_metadata']['principal'])

    @browsing
    def test_updating_a_document_via_webdav_creates_initial_version_too(self, browser):
        self.login(self.regular_user)

        versioner = Versioner(self.document)
        self.assertFalse(versioner.has_initial_version())

        writer = IRawWriteFile(self.document, None)
        writer.write('New Data')
        writer.close()

        self.assertTrue(versioner.has_initial_version())
        self.assertEquals(
            1, versioner.get_history_metadata().getLength(countPurged=False))

    @browsing
    def test_custom_comment_is_used_when_creating_initial_version(self, browser):
        self.login(self.regular_user)

        versioner = Versioner(self.document)
        versioner.set_custom_initial_version_comment(u'custom initial version')

        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')

        version = versioner.retrieve_version(0)
        self.assertEquals(
            u'custom initial version', version.sys_metadata['comment'])

        self.assertIsNone(versioner.get_custom_initial_version_comment())

    def test_fetching_version_metadata(self):
        self.login(self.regular_user)
        versioner = Versioner(self.document)
        versioner.set_custom_initial_version_comment(u'custom initial version')
        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')
        sys_metadata = versioner.get_version_metadata(0).get('sys_metadata')
        self.assertEqual(u'custom initial version', sys_metadata.get('comment'))
        self.assertEqual('robert.ziegler', sys_metadata.get('principal'))
        self.assertEqual('document-state-draft', sys_metadata.get('review_state'))
