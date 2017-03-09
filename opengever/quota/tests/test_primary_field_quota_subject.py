from ftw.builder import Builder
from opengever.trash.trash import ITrashable
from ftw.builder import create
from opengever.quota.interfaces import IQuotaSubject
from opengever.testing import FunctionalTestCase


class TestPrimaryFieldQuotaSubject(FunctionalTestCase):

    def test_get_size_on_document(self):
        self.grant('Manager')
        document = create(Builder('document')
                          .attach_file_containing('Hello World'))
        self.assertEquals(11, IQuotaSubject(document).get_size())

        ITrashable(document).trash()
        self.assertEquals(0, IQuotaSubject(document).get_size())

    def test_get_size_on_mails(self):
        self.grant('Manager')
        mail = create(Builder('mail')
                          .with_message('Not really an email'))
        self.assertEquals(19, IQuotaSubject(mail).get_size())

        ITrashable(mail).trash()
        self.assertEquals(0, IQuotaSubject(mail).get_size())
