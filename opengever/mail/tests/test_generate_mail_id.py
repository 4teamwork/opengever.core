from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
import os

MAIL_DATA = open(
    os.path.join(os.path.dirname(__file__), 'mail.txt'), 'r').read()


class TestGenerateMailIdAndSequentialNumber(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestGenerateMailIdAndSequentialNumber, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

    def test_generate_mail_id_with_sequencenumber(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        document = create(Builder("document"))

        self.assertEquals('document-1', mail.getId())
        self.assertEquals('document-2', document.getId())
