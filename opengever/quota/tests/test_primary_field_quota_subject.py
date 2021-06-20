from ftw.builder import Builder
from ftw.builder import create
from opengever.quota.interfaces import IObjectSize
from opengever.testing import FunctionalTestCase
from opengever.trash.trash import ITrasher


class TestPrimaryFieldQuotaSubject(FunctionalTestCase):

    def test_get_size_on_document(self):
        self.grant('Manager')
        document = create(Builder('document')
                          .attach_file_containing('Hello World'))
        self.assertEquals(11, IObjectSize(document).get_size())

        ITrasher(document).trash()
        self.assertEquals(0, IObjectSize(document).get_size())

    def test_get_size_on_mails(self):
        self.grant('Manager')
        mail = create(Builder('mail')
                          .with_message('Not really an email'))
        self.assertEquals(19, IObjectSize(mail).get_size())

        ITrasher(mail).trash()
        self.assertEquals(0, IObjectSize(mail).get_size())
