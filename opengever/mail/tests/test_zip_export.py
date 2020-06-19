from ftw.zipexport.interfaces import IZipRepresentation
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestMailZipExport(IntegrationTestCase):
    def test_download_eml_if_there_is_no_msg(self):
        self.login(self.dossier_responsible)
        representation = getMultiAdapter((self.mail_eml, self.request),
                                         interface=IZipRepresentation)

        path, file_ = tuple(representation.get_files())[0]
        self.assertEquals(u'/Die Buergschaft.eml', path)
        self.assertEquals(self.mail_eml.message.open().read(),
                          file_.read())

    def test_download_msg_if_there_is_a_original_message(self):
        self.login(self.dossier_responsible)
        representation = getMultiAdapter((self.mail_msg, self.request),
                                         interface=IZipRepresentation)

        path, file_ = tuple(representation.get_files())[0]
        self.assertEquals(u'/No Subject.msg', path)
        self.assertEquals(self.mail_msg.original_message.open().read(),
                          file_.read())
