from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from opengever.base.command import CreateEmailCommand
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_string
from plone.app.testing import TEST_USER_ID
from zope.annotation import IAnnotations
from zope.i18n import translate
import transaction


MAIL_DATA_LF = resource_string('opengever.mail.tests', 'mail_lf.txt')
MAIL_DATA_CRLF = resource_string('opengever.mail.tests', 'mail_crlf.txt')


class TestMailDownloadCopy(FunctionalTestCase):
    """Test downloading a mail works."""

    @browsing
    def test_mail_download_copy_yields_correct_headers(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        DownloadConfirmationHelper(mail).deactivate()
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset({
            'status': '200 Ok',
            'content-length': str(len(browser.contents)),
            'content-type': 'message/rfc822',
            'content-disposition': 'attachment; filename="Die Buergschaft.eml"',
            },
            browser.headers)

    @browsing
    def test_mail_download_copy_causes_journal_entry(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        DownloadConfirmationHelper(mail).deactivate()
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        def get_journal(obj):
            annotations = IAnnotations(mail)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, {})

        journal = get_journal(mail)
        last_entry = journal[-1]

        self.assertEquals(TEST_USER_ID, last_entry['actor'])

        action = last_entry['action']
        self.assertDictContainsSubset(
            {'type': 'File copy downloaded',
             'title': u'label_file_copy_downloaded'},
            action)

        self.assertEquals(u'Download copy', translate(action['title']))

    @browsing
    def test_mail_download_converts_lf_to_crlf(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA_LF))
        DownloadConfirmationHelper(mail).deactivate()
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertTrue(
            browser.contents.startswith(
                'Return-Path: <James.Bond@test.ch>\r\n'),
            'Lineendings are not converted correctly.')

    @browsing
    def test_mail_download_handles_crlf_correctly(self, browser):
        """Mails with already CRLF, should not be converted or changed.
        """
        mail = create(Builder("mail").with_message(MAIL_DATA_CRLF))
        DownloadConfirmationHelper(mail).deactivate()
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertTrue(
            browser.contents.startswith(
                'Return-Path: <James.Bond@example.org>\r\n'),
            'Lineendings are not converted correctly.')

    @browsing
    def test_mail_download_links_never_have_confirmation(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA_CRLF))
        dch = DownloadConfirmationHelper(mail)

        browser.login()
        browser.open(mail, view='tabbedview_view-overview')
        self.assertNotIn(
            'confirmation',
            browser.css('a.function-download-copy').first.get('href'))

        dch.deactivate()
        browser.open(mail, view='tabbedview_view-overview')
        self.assertNotIn(
            'confirmation',
            browser.css('a.function-download-copy').first.get('href'))

    @browsing
    def test_download_copy_delivers_msg_if_available(self, browser):
        msg_data = 'mock-msg-body'

        dossier = create(Builder('dossier'))

        class MockMsg2MimeTransform(object):

            def transform(self, data):
                return 'mock-eml-body'

        command = CreateEmailCommand(dossier,
                                     'testm\xc3\xa4il.msg',
                                     msg_data,
                                     transform=MockMsg2MimeTransform())
        mail = command.execute()
        transaction.commit()

        DownloadConfirmationHelper(mail).deactivate()
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset({
            'status': '200 Ok',
            'content-length': str(len(browser.contents)),
            'content-type': 'application/vnd.ms-outlook',
            'content-disposition': 'attachment; filename="No Subject.msg"',
            },
            browser.headers)

        self.assertEquals(msg_data, browser.contents)
