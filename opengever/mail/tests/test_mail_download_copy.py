from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_string
from plone.app.testing import TEST_USER_ID
from zope.annotation import IAnnotations
from zope.i18n import translate


MAIL_DATA = resource_string('opengever.mail.tests', 'mail.txt')


class TestMailDownloadCopy(FunctionalTestCase):

    def setUp(self):
        super(TestMailDownloadCopy, self).setUp()
        self.grant('Manager')

    @browsing
    def test_mail_download_copy_yields_correct_headers(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        browser.login().visit(mail, view='tabbedview_view-overview')
        browser.find('Download copy').click()

        self.assertDictContainsSubset({
            'status': '200 Ok',
            'content-length': str(len(MAIL_DATA)),
            'content-type': 'message/rfc822',
            'content-disposition': 'attachment; filename="testmail.eml"'},
            browser.headers)

    @browsing
    def test_mail_download_copy_causes_journal_entry(self, browser):
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
