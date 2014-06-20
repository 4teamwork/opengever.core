from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail import utils
from opengever.document.behaviors import metadata
from opengever.document.interfaces import IDocumentSettings
from opengever.testing import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import os


MAIL_DATA = open(
    os.path.join(os.path.dirname(__file__), 'mail.txt'), 'r').read()


class TestMailMetadata(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestMailMetadata, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

    def get_header_date(self, mail):
        return datetime.fromtimestamp(utils.get_date_header(mail.msg, 'Date'))

    def get_preserved_as_papger_default(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(
            IDocumentSettings).preserved_as_paper_default

    def test_fill_metadata_of_new_mail(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        mail_metadata = metadata.IDocumentMetadata(mail)

        self.assertIsNone(mail_metadata.description,
                          'Description has no value')

        self.assertEquals((), mail_metadata.keywords, 'Expect no keywords')

        self.assertIsNone(mail_metadata.foreign_reference,
                          'Foreign reference has no value')

        self.assertEquals(self.get_header_date(mail).date(),
                          mail_metadata.document_date)

        self.assertIsNone(mail_metadata.delivery_date,
                          'Delivery date has no value')

        # XXX: mle: Does not make any sense to me.
        # self.assertEquals(mail.message, mail_metadata.archival_file)

        self.assertEquals(self.get_preserved_as_papger_default(),
                          mail_metadata.preserved_as_paper)
