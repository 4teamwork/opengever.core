from datetime import datetime
from ftw.testbrowser import browsing
from opengever.document.versioner import Versioner
from opengever.dossier.docprops import DocPropertyWriter
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
