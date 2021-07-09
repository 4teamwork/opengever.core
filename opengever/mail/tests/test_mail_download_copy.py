from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.journal.tests.utils import get_journal_entry
from opengever.mail.interfaces import IMailDownloadSettings
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_string
from plone import api
from zope.i18n import translate


MAIL_DATA_LF = resource_string('opengever.mail.tests', 'mail_lf.txt')
MAIL_DATA_CRLF = resource_string('opengever.mail.tests', 'mail_crlf.txt')


class TestMailDownloadCopy(IntegrationTestCase):
    """Test downloading a mail works."""

    @browsing
    def test_mail_download_copy_yields_correct_headers(self, browser):
        self.login(self.regular_user, browser=browser)

        DownloadConfirmationHelper(self.mail_eml).deactivate()
        browser.visit(self.mail_eml, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset(
            {'content-length': str(len(browser.contents)),
             'content-type': 'message/rfc822',
             'content-disposition': 'attachment; filename="Die Buergschaft.eml"'},
            browser.headers)

    @browsing
    def test_mail_download_copy_causes_journal_entry(self, browser):
        self.login(self.regular_user, browser=browser)

        DownloadConfirmationHelper(self.mail_eml).deactivate()
        browser.visit(self.mail_eml, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        last_entry = get_journal_entry(self.mail_eml, -1)
        self.assertEquals(self.regular_user.id, last_entry['actor'])

        action = last_entry['action']
        self.assertDictContainsSubset(
            {'type': 'File copy downloaded',
             'title': u'label_file_copy_downloaded'},
            action)

        self.assertEquals(u'Document copy downloaded', translate(action['title']))

    @browsing
    def test_mail_download_converts_lf_to_crlf(self, browser):
        self.login(self.regular_user, browser=browser)

        mail = create(Builder("mail")
                      .within(self.dossier)
                      .with_message(MAIL_DATA_LF))
        DownloadConfirmationHelper(mail).deactivate()
        browser.visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertTrue(
            browser.contents.startswith(
                'Return-Path: <James.Bond@test.ch>\r\n'),
            'Lineendings are not converted correctly.')

    @browsing
    def test_mail_download_handles_crlf_correctly(self, browser):
        """Mails with already CRLF, should not be converted or changed.
        """
        self.login(self.regular_user, browser=browser)

        mail = create(Builder("mail")
                      .within(self.dossier)
                      .with_message(MAIL_DATA_CRLF))
        DownloadConfirmationHelper(mail).deactivate()
        browser.visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertTrue(
            browser.contents.startswith(
                'Return-Path: <James.Bond@example.org>\r\n'),
            'Lineendings are not converted correctly.')

    @browsing
    def test_mail_download_links_never_have_confirmation(self, browser):
        self.login(self.regular_user, browser=browser)

        dch = DownloadConfirmationHelper(self.mail_eml)

        browser.open(self.mail_eml, view='tabbedview_view-overview')
        self.assertNotIn(
            'confirmation',
            browser.css('a.function-download-copy').first.get('href'))

        dch.deactivate()
        browser.open(self.mail_eml, view='tabbedview_view-overview')
        self.assertNotIn(
            'confirmation',
            browser.css('a.function-download-copy').first.get('href'))

    @browsing
    def test_download_copy_delivers_msg_if_available(self, browser):
        self.login(self.regular_user, browser=browser)

        DownloadConfirmationHelper(self.mail_msg).deactivate()
        browser.visit(self.mail_msg, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset({
            'content-length': str(len(browser.contents)),
            'content-type': 'application/vnd.ms-outlook',
            'content-disposition': 'attachment; filename="No Subject.msg"',
            },
            browser.headers)

        self.assertEquals(self.mail_msg.original_message.data, browser.contents)

    @browsing
    def test_download_copy_changes_p7m_extension_to_eml(self, browser):
        self.login(self.regular_user, browser=browser)

        mail_p7m = create(Builder('mail')
                          .within(self.dossier)
                          .with_asset_message('signed.p7m'))

        browser.visit(mail_p7m, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset(
            {'content-length': str(len(browser.contents)),
             'content-type': 'application/pkcs7-mime',
             'content-disposition': 'attachment; filename="Hello.eml"'},
            browser.headers)

        self.assertEquals(
            mail_p7m.get_file().data.replace("\r", "").replace("\n", ""),
            browser.contents.replace("\r", "").replace("\n", ""))

    @browsing
    def test_download_copy_respects_p7m_extension_replacement_setting(self, browser):
        self.login(self.regular_user, browser=browser)

        api.portal.set_registry_record(
            'p7m_extension_replacement', u'foo', IMailDownloadSettings)
        mail_p7m = create(Builder('mail')
                          .within(self.dossier)
                          .with_asset_message('signed.p7m'))

        browser.visit(mail_p7m, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset(
            {'content-length': str(len(browser.contents)),
             'content-type': 'application/pkcs7-mime',
             'content-disposition': 'attachment; filename="Hello.foo"'},
            browser.headers)
