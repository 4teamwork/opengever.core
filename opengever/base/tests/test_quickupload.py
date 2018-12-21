from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from opengever.journal.browser import JournalHistory
from opengever.testing import IntegrationTestCase
from zope.i18n import translate


class TestOGQuickupload(IntegrationTestCase):

    def setUp(self):
        super(TestOGQuickupload, self).setUp()

        self.login(self.regular_user)
        self.adapter = IQuickUploadFileFactory(self.dossier)

    def test_get_mimetype(self):
        self.assertEqual('application/msword',
                         self.adapter._get_mimetype('.doc'))
        self.assertEqual('image/jpeg',
                         self.adapter._get_mimetype('.jpeg'))

    def test_is_email_upload(self):
        self.assertTrue(self.adapter.is_email_upload('mail.msg'))
        self.assertTrue(self.adapter.is_email_upload('mail.eml'))

        self.assertFalse(self.adapter.is_email_upload('image.jpeg'))
        self.assertFalse(self.adapter.is_email_upload('test.doc'))

    def test_set_default_values(self):
        content = create(Builder('quickuploaded_document')
                         .within(self.dossier)
                         .with_data('text'))

        self.assertEquals('document', content.Title())
        self.assertEquals('text', content.file.data)
        self.assertEquals(u'', content.description)

    def test_expect_one_journal_entry_after_upload(self):
        content = create(Builder('quickuploaded_document')
                         .within(self.dossier)
                         .with_asset_data('text.txt'))

        history = JournalHistory(content, content.REQUEST)
        self.assertEquals(1,
                          len(history.data()),
                          'Expect exactly one journal entry after upload')

    def test_title_is_used_as_default_title_for_journal_entry(self):
        content = create(Builder('quickuploaded_document')
                         .within(self.dossier)
                         .with_data('text'))
        history = JournalHistory(content, content.REQUEST)

        self.assertEquals(u'Document added: document',
                          translate(history.data()[0]['action']['title']),
                          'Expected the document title in the action title')
