from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.journal.browser import JournalHistory
from opengever.propertysheets.storage import PropertySheetSchemaStorage
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
        self.assertTrue(self.adapter.is_email_upload('mail.p7m'))

        self.assertFalse(self.adapter.is_email_upload('image.jpeg'))
        self.assertFalse(self.adapter.is_email_upload('test.doc'))

    def test_set_default_values(self):
        content = create(Builder('quickuploaded_document')
                         .within(self.dossier)
                         .with_data('text'))

        self.assertEquals('document', content.Title())
        self.assertEquals('text', content.file.data)
        self.assertEquals(u'', content.description)

    def test_set_custom_properties_default_values(self):
        self.login(self.regular_user)
        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'textline', u'notrequired', u'Optional field with default', u'',
                required=False,
                default=u'Not required, still has default'
            )
            .with_field(
                'multiple_choice', u'languages', u'Languages', u'',
                required=True, values=[u'de', u'fr', u'en'],
                default={u'de', u'en'},
            )
        )

        content = create(Builder('quickuploaded_document')
                         .within(self.dossier)
                         .with_data('text'))

        expected_defaults = {
            u'IDocument.default': {
                u'languages': [u'de', u'en'],
                u'notrequired': u'Not required, still has default',
            },
        }
        self.assertEqual(
            expected_defaults,
            IDocumentCustomProperties(content).custom_properties)

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

    def test_uses_mimetype_from_mimetype_registry(self):
        content = create(Builder('quickuploaded_document')
                         .within(self.dossier)
                         .with_data(
                            'Cadwork 2d Dummy document',
                            filename='test.2d',
                            content_type='application/x-cadwork-2d'))
        self.assertEqual(content.file.contentType, 'application/x-cadwork-2d')
