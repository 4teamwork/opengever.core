from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.mail.utils import get_attachments
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.mail.browser.extract_attachments import content_type_helper
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from pkg_resources import resource_string
from plone.app.testing import TEST_USER_ID
from zope.annotation import IAnnotations
from zope.i18n import translate


MESSAGE_TEXT = 'Mime-Version: 1.0\nContent-Type: multipart/mixed; boundary=908752978\nTo: to@example.org\nFrom: from@example.org\nSubject: Attachment Test\nDate: Thu, 01 Jan 1970 01:00:00 +0100\nMessage-Id: <1>\n\n\n--908752978\nContent-Disposition: attachment;\n	filename*=iso-8859-1\'\'B%FCcher.txt\nContent-Type: text/plain;\n	name="=?iso-8859-1?Q?B=FCcher.txt?="\nContent-Transfer-Encoding: base64\n\nw6TDtsOcCg==\n\n--908752978--\n'
MAIL_DATA_WRONG_MIMETYPE = resource_string(
    'opengever.mail.tests', 'attachment_with_wrong_mimetype.txt')


class TestExtractAttachmentView(FunctionalTestCase):

    def setUp(self):
        super(TestExtractAttachmentView, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.mail = create(Builder('mail')
                           .within(self.dossier)
                           .with_message(MESSAGE_TEXT))

    @browsing
    def test_without_selecting_attachments_shows_error_statusmessage(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        browser.forms.get('form').submit()

        self.assertEquals(['You have not selected any attachments.'],
                          statusmessages.messages().get('error'))
        self.assertEquals(
            'http://nohost/plone/dossier-1/document-1/extract_attachments',
            browser.url)

    @browsing
    def test_extract_attachments_can_handle_attachment_with_wrong_mimetype(self, browser):
        # When rewriting as integration layer, use change_mail_data here
        mail = create(
            Builder("mail").with_message(MAIL_DATA_WRONG_MIMETYPE))
        browser.login().open(mail, view='extract_attachments')
        self.assertIsNotNone(browser.css('.icon-dokument_verweis'))
        self.assertEquals([u'B\xfccher.txt'],
                          browser.css('.listing td a').text)

    @browsing
    def test_shows_info_statusmessage_by_success(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        browser.fill({'attachments:list': ['1']}).submit()

        self.assertEquals([u'Created document B\xfccher'],
                          statusmessages.messages().get('info'))
        self.assertEquals('http://nohost/plone/dossier-1/#documents',
                          browser.url)

    @browsing
    def test_creates_document_in_parent_dossier(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        browser.fill({'attachments:list': ['1']}).submit()

        doc = self.dossier.listFolderContents(
            {'portal_type': 'opengever.document.document'})[0]

        self.assertEquals('B\xc3\xbccher', doc.Title())
        self.assertEquals(doc.document_date, date.today())

        self.assertEquals(obj2brain(doc).document_date, date.today())

    @browsing
    def test_deleting_after_extracting(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        browser.fill({'attachments:list': ['1'],
                      'delete_action': ['all']}).submit()

        self.assertEquals(
            len(get_attachments(self.mail.msg)), 0,
            'The attachment deleting after extracting, \
            does not work correctly.')

    @browsing
    def test_deleting_after_extracting_updates_checksum(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        old_checksum = IBumblebeeDocument(self.mail).get_checksum()
        browser.fill({'attachments:list': ['1'],
                      'delete_action': ['all']}).submit()
        new_checksum = IBumblebeeDocument(self.mail).get_checksum()
        self.assertNotEqual(old_checksum, new_checksum)

    @browsing
    def test_journal_entry_after_deleting_attachments(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        browser.fill({'attachments:list': ['1'],
                      'delete_action': ['all']}).submit()

        annotations = IAnnotations(self.mail)
        journal = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, {})
        last_entry = journal[-1]

        self.assertEquals(TEST_USER_ID, last_entry['actor'])
        self.assertDictContainsSubset(
            {'type': 'Attachments deleted',
             'title': u'label_attachments_deleted'},
            last_entry['action'])
        self.assertEquals(u'Attachments deleted: B\xfccher.txt',
                          translate(last_entry['action']['title']))

    @browsing
    def test_extract_attachment_without_docs_shows_warning_message(self, browser):
        mail = create(Builder('mail').within(self.dossier))
        browser.login().open(mail, view='extract_attachments')

        self.assertEquals(['This mail has no attachments to extract.'],
                          statusmessages.messages().get('warning'))
        self.assertEquals(mail.absolute_url(), browser.url)

    @browsing
    def test_cancel_redirects_to_mail(self, browser):
        browser.login().open(self.mail, view='extract_attachments')
        browser.css('.formControls input.standalone').first.click()

        self.assertEquals(self.mail.absolute_url(), browser.url)


class TestExtractAttachmentViewForMailWithOriginalMessage(FunctionalTestCase):

    def setUp(self):
        super(TestExtractAttachmentViewForMailWithOriginalMessage, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.mail = create(Builder('mail')
                           .within(self.dossier)
                           .with_message(MESSAGE_TEXT)
                           .with_dummy_original_message())

    @browsing
    def test_deleting_after_extracting_does_not_update_checksum(self, browser):
        """ We use the original message for preview but deleting the attachments
        after extraction modifies the message and not the original_message, hence
        the checksum nor the preview will be modified.
        """
        browser.login().open(self.mail, view='extract_attachments')
        old_checksum = IBumblebeeDocument(self.mail).get_checksum()
        browser.fill({'attachments:list': ['1'],
                      'delete_action': ['all']}).submit()
        new_checksum = IBumblebeeDocument(self.mail).get_checksum()
        self.assertEqual(old_checksum, new_checksum)


class TestContentTypeHelper(FunctionalTestCase):

    def test_lookup_the_contenttype(self):
        self.assertEquals(
            '<span class=icon-image />',
            content_type_helper({}, 'image/gif'))

        # default for unknown types
        self.assertEquals(
            '<span class=icon-dokument_verweis />',
            content_type_helper({}, 'something/unknown'))

    def test_lookup_via_filename_when_contenttype_is_octet_stream(self):
        item = {'position': 5,
                'size': 1835,
                'content-type': 'application/octet-stream',
                'filename': 'ATT00001.gif'}

        self.assertEquals(
            '<span class=icon-image />',
            content_type_helper(item, 'application/octet-stream'))
