from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from opengever.journal.browser import JournalHistory
from opengever.testing import FunctionalTestCase
from zope.i18n import translate


class TestOGQuickupload(FunctionalTestCase):

    def setUp(self):
        super(TestOGQuickupload, self).setUp()
        self.grant('Manager')
        self.dossier = create(Builder('dossier'))
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
        result = self.adapter(filename='document.txt',
                              title='',  # ignored by adapter
                              description='Description',  # ignored by adapter
                              content_type='text/plain',
                              data='text',
                              portal_type='opengever.document.document')
        content = result['success']

        self.assertEquals('document', content.Title())
        self.assertEquals('text', content.file.data)
        self.assertIsNone(content.description)

    def test_expect_one_journal_entry_after_upload(self):
        result = self.adapter(filename='document.txt',
                              title='Title of document',
                              description='',
                              content_type='text/plain',
                              data='text',
                              portal_type='opengever.document.document')
        content = result['success']
        history = JournalHistory(content, content.REQUEST)

        self.assertEquals(1,
                          len(history.data()),
                          'Expect exactly one journal entry after upload')

    def test_title_is_used_as_default_title_for_journal_entry(self):
        result = self.adapter(filename='document.txt',
                              title='',
                              description='',
                              content_type='text/plain',
                              data='text',
                              portal_type='opengever.document.document')
        content = result['success']
        history = JournalHistory(content, content.REQUEST)

        self.assertEquals(u'Document added: document',
                          translate(history.data()[0]['action']['title']),
                          'Expected the document title in the action title')
