from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.tests.test_archival_file import TestArchivalFile


class TestArchivalFileForMails(TestArchivalFile):

    def setUp(self):
        super(TestArchivalFileForMails, self).setUp()
        self.login(self.regular_user)
        self.test_document = self.mail_eml

    def test_file_name_is_file_filename_with_pdf_extension(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'Die Buergschaft.pdf',
            ArchivalFileConverter(self.test_document).get_file_name())
