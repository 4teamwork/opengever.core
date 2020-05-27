from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.security import elevated_privileges
from opengever.testing import FunctionalTestCase
from plone import api
from plone.uuid.interfaces import IUUID
import transaction


class TestSubscribers(FunctionalTestCase):
    """Test mail update events fire as designed."""

    def setUp(self):
        super(TestSubscribers, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier').within(self.repo))
        self.mail = create(Builder('mail')
                           .within(self.dossier)
                           .with_asset_message(
                               'mail_with_multiple_attachments.eml'))

    @browsing
    def test_modifying_title_updates_filename(self, browser):
        browser.login().open(self.mail, view='edit')
        browser.fill({'Title': 'My new mail Title'}).submit()

        self.assertEqual(u'My new mail Title.eml', self.mail.message.filename)

    def test_attachment_info_is_updated_when_extracted_document_is_moved(self):
        self.destination_dossier = create(Builder('dossier'))
        self.login()

        doc = self.mail.extract_attachment_into_parent(4)
        transaction.commit()
        doc_url = doc.absolute_url()

        info = self.mail._get_attachment_info(4)
        self.assertEqual(doc_url, info.get("extracted_document_url"))

        moved_doc = api.content.move(doc, self.destination_dossier)

        info = self.mail._get_attachment_info(4)
        self.assertNotEqual(doc_url, moved_doc.absolute_url())
        self.assertEqual(moved_doc.absolute_url(),
                         info.get("extracted_document_url"))

    @browsing
    def test_attachment_info_is_updated_when_extracted_document_is_deleted(self, browser):
        self.login()
        doc = self.mail.extract_attachment_into_parent(4)
        transaction.commit()

        info = self.mail._get_attachment_info(4)
        self.assertTrue(info.get("extracted"))
        self.assertEqual(doc.absolute_url(), info.get("extracted_document_url"))
        self.assertEqual(IUUID(doc), info.get("extracted_document_uid"))

        with elevated_privileges():
            api.content.delete(doc)

        info = self.mail._get_attachment_info(4)
        self.assertFalse(info.get("extracted"))
        self.assertIsNone(info.get("extracted_document_url"))
        self.assertIsNone(info.get("extracted_document_uid"))
