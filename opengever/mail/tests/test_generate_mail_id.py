from ftw.builder import Builder
from ftw.builder import create
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase


class TestGenerateMailIdAndSequentialNumber(FunctionalTestCase):
    use_browser = True

    def test_generate_mail_id_with_sequencenumber(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        document = create(Builder("document"))

        self.assertEquals('document-1', mail.getId())
        self.assertEquals('document-2', document.getId())
