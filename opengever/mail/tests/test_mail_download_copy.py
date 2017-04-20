from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_string
from plone.app.testing import TEST_USER_ID
from zope.annotation import IAnnotations
from zope.i18n import translate


MAIL_DATA_LF = resource_string('opengever.mail.tests', 'mail_lf.txt')
MAIL_DATA_CRLF = resource_string('opengever.mail.tests', 'mail_crlf.txt')


class TestMailDownloadCopy(FunctionalTestCase):

    @browsing
    def test_mail_download_copy_yields_correct_headers(self, browser):
        DownloadConfirmationHelper().deactivate()
        mail = create(Builder("mail").with_message(MAIL_DATA))
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset({
            'status': '200 Ok',
            'content-length': str(len(browser.contents)),
            'content-type': 'message/rfc822',
            'content-disposition': 'attachment; filename="die-burgschaft.eml"'},
            browser.headers)

    @browsing
    def test_mail_download_copy_causes_journal_entry(self, browser):
        DownloadConfirmationHelper().deactivate()
        mail = create(Builder("mail").with_message(MAIL_DATA))
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

        self.assertEquals(u'Download copy',
                          translate(action['title']))

    @browsing
    def test_mail_download_converts_lf_to_crlf(self, browser):
        DownloadConfirmationHelper().deactivate()
        mail = create(Builder("mail").with_message(MAIL_DATA_LF))
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertTrue(
            browser.contents.startswith('Return-Path: <James.Bond@test.ch>\r\n'),
            'Lineendings are not converted correctly.')

    @browsing
    def test_mail_download_handles_crlf_correctly(self, browser):
        """Mails with already CRLF, should not be converted or changed.
        """
        DownloadConfirmationHelper().deactivate()
        mail = create(Builder("mail").with_message(MAIL_DATA_CRLF))
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertTrue(
            browser.contents.startswith('Return-Path: <James.Bond@example.org>\r\n'),
            'Lineendings are not converted correctly.')
