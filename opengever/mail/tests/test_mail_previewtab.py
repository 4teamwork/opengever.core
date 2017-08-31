from ftw.testbrowser import browsing
from opengever.mail.tests import MAIL_DATA
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_string


class TestPreviewTab(IntegrationTestCase):

    @browsing
    def test_mail_preview_tab(self, browser):
        self.login(self.regular_user, browser)
        self.change_mail_data(self.mail, MAIL_DATA)

        browser.open(self.mail, view='tabbedview_view-preview')

        expect = [['From:', u'Freddy H\xf6lderlin <from@example.org>'],
                  ['Subject:', u'Die B\xfcrgschaft'],
                  ['Date:', 'Jan 01, 1999 01:00 AM'],
                  ['To:', u'Christoph M\xf6rgeli <to@example.org>']]
        self.assertEquals(expect,
                          browser.css('.mailHeaders.listing').first.lists())

    @browsing
    def test_preview_tab_can_handle_attachment_with_wrong_mimetype(self, browser):
        self.login(self.regular_user, browser)
        mail_data = resource_string('opengever.mail.tests',
                                    'attachment_with_wrong_mimetype.txt')
        self.change_mail_data(self.mail, mail_data)

        browser.open(self.mail, view='tabbedview_view-preview')

        self.assertEquals([u'B\xfccher.txt'],
                          browser.css('div.mailAttachment a').text)
