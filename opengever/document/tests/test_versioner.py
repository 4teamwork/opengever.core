from datetime import datetime
from ftw.testbrowser import browsing
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile


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
        self.assertEquals(1, versioner._get_history().getLength(countPurged=False))

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
