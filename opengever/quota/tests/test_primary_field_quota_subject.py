from ftw.builder import Builder
from ftw.builder import create
from opengever.quota.interfaces import IQuotaSubject
from opengever.testing import FunctionalTestCase


class TestPrimaryFieldQuotaSubject(FunctionalTestCase):

    def test_get_size_on_document(self):
        document = create(Builder('document')
                          .attach_file_containing('Hello World'))
        self.assertEquals(11, IQuotaSubject(document).get_size())

    def test_get_size_on_mails(self):
        document = create(Builder('mail')
                          .with_message('Not really an email'))
        self.assertEquals(19, IQuotaSubject(document).get_size())
