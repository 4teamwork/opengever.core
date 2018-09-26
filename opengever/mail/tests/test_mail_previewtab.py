from ftw.testbrowser import browsing
from opengever.mail.interfaces import IMailTabbedviewSettings
from opengever.mail.tests import MAIL_DATA
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_string
from plone import api


class TestPreviewTab(IntegrationTestCase):

    @browsing
    def test_mail_preview_tab(self, browser):
        self.login(self.regular_user, browser)
        self.change_mail_data(self.mail_eml, MAIL_DATA)

        browser.open(self.mail_eml, view='tabbedview_view-preview')

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
        self.change_mail_data(self.mail_eml, mail_data)

        browser.open(self.mail_eml, view='tabbedview_view-preview')

        self.assertEquals([u'B\xfccher.txt'],
                          browser.css('div.mailAttachment a').text)

    @browsing
    def test_preview_tab_can_be_disabled_by_registry_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view='tabbed_view')

        self.assertEquals(
            ['Overview', 'Preview', 'Journal', 'Sharing'],
            browser.css('.formTab').text)

        api.portal.set_registry_record(
            name='preview_tab_visible', interface=IMailTabbedviewSettings,
            value=False)

        browser.open(self.mail_eml, view='tabbed_view')
        self.assertEquals(
            ['Overview', 'Journal', 'Sharing'],
            browser.css('.formTab').text)
