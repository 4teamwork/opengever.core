from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
import os

MAIL_DATA = open(
    os.path.join(os.path.dirname(__file__), 'mail.txt'), 'r').read()


class TestPreview(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestPreview, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

    @browsing
    def test_mail_preview_tab(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        browser.login().visit(mail, view='tabbedview_view-preview')

        expect = [['From:', 'from@example.org'],
                  ['Subject:', u'Die B\xfcrgschaft'],
                  ['Date:', 'Jan 01, 1970 01:00 AM'],
                  ['To:', u'Friedrich H\xf6lderlin <to@example.org>']]
        self.assertEquals(expect,
                          browser.css('.mailHeaders.listing').first.lists())
