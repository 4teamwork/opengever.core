from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestCheckedOutViewlet(FunctionalTestCase):

    @browsing
    def test_viewlet_show_msg_when_document_is_checked_out(self, browser):
        document = create(Builder('document')
                          .titled(u'TestDocument')
                          .checked_out_by(TEST_USER_ID))

        browser.login().open(document)

        message = browser.css('dl.checked_out_viewlet dd').first
        link = browser.css('dl.checked_out_viewlet a').first

        self.assertEqual('This item is being checked out by Test User (test_user_1_).',
                         message.text)
        self.assertEqual('http://nohost/plone/@@user-details/test_user_1_',
                         link.get('href'))

    @browsing
    def test_viewlet_is_disabled_when_document_is_not_checked_out(self, browser):
        document = create(Builder('document').titled(u'TestDocument'))
        browser.login().open(document)

        self.assertEqual([],
                         browser.css('dl.checked_out_viewlet'))
