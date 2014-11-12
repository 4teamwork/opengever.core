from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.mail.utils import get_attachments
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.document.interfaces import IDocumentSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.i18n import translate
import transaction


MESSAGE_TEXT = 'Mime-Version: 1.0\nContent-Type: multipart/mixed; boundary=908752978\nTo: to@example.org\nFrom: from@example.org\nSubject: Attachment Test\nDate: Thu, 01 Jan 1970 01:00:00 +0100\nMessage-Id: <1>\n\n\n--908752978\nContent-Disposition: attachment;\n	filename*=iso-8859-1\'\'B%FCcher.txt\nContent-Type: text/plain;\n	name="=?iso-8859-1?Q?B=FCcher.txt?="\nContent-Transfer-Encoding: base64\n\nw6TDtsOcCg==\n\n--908752978--\n'

LINEBREAK_MESSAGETEXT = """Mime-Version: 1.0
Content-Type: multipart/mixed; boundary=908752978
To: to@example.org\nFrom: from@example.org
Subject: Attachment Test
Date: Thu, 01 Jan 1970 01:00:00 +0100\nMessage-Id: <1>


--908752978
Content-Disposition: attachment;
	filename=Projekt Test Inputvorschlag.doc
Content-Type: text/plain;
	name="Projekt Test Input
        vorschlag.doc"
Content-Transfer-Encoding: base64

w6TDtsOcCg==

--908752978--
"""


class TestAttachmentExtraction(FunctionalTestCase):

    def setUp(self):
        super(TestAttachmentExtraction, self).setUp()

        self.grant('Owner', 'Editor', 'Contributor', 'Manager')

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
    def test_sets_default_values_correctly_on_document(self, browser):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDocumentSettings)
        proxy.preserved_as_paper_default = False
        transaction.commit()

        browser.login().open(self.mail, view='extract_attachments')
        browser.fill({'attachments:list': ['1']}).submit()

        doc = self.dossier.listFolderContents(
            {'portal_type': 'opengever.document.document'})[0]
        self.assertFalse(doc.preserved_as_paper)
        self.assertTrue(doc.digitally_available)

    @browsing
    def test_extracting_line_break_mail(self, browser):
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_message(LINEBREAK_MESSAGETEXT))

        browser.login().open(mail, view='extract_attachments')
        browser.fill({'attachments:list': ['1']}).submit()

        doc = self.dossier.listFolderContents(
            {'portal_type': 'opengever.document.document'})[0]
        self.assertEquals('Projekt Test Inputvorschlag', doc.Title())

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
    def test_extract_attachment_without_docs_shows_waring_statusmessage(self, browser):
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
