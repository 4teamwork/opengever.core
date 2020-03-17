from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestCheckedOutViewlet(IntegrationTestCase):

    @browsing
    def test_viewlet_show_msg_when_document_is_checked_out(self, browser):
        self.login(self.regular_user, browser)

        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        browser.open(self.document)

        message = browser.css('dl.checked_out_viewlet dd').first
        link = browser.css('dl.checked_out_viewlet a').first

        self.assertEqual(u'This item is being checked out by B\xe4rfuss K\xe4thi (kathi.barfuss).',
                         message.text)
        self.assertEqual('http://nohost/plone/@@user-details/kathi.barfuss',
                         link.get('href'))

    @browsing
    def test_viewlet_is_disabled_when_document_is_not_checked_out(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document)
        self.assertEqual([], browser.css('dl.checked_out_viewlet'))
