from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.pages.statusmessages import assert_message
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestForceCheckin(IntegrationTestCase):
    """Force checkin is the description for checking in a document which has
    been checked out by another user.
    """

    @browsing
    def test_is_possible_for_administrators(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)

        # checkout
        browser.open(self.document)
        browser.click_on('Check out')
        self.assertEquals(self.dossier_responsible.getId(),
                          manager.get_checked_out_by())
        assert_message(u'Checked out: Vertr\xe4gsentwurf')

        # force checkin as administrator
        self.login(self.administrator, browser=browser)
        browser.open(self.document)
        browser.click_on('without comment')

        assert_message(u'Checked in: Vertr\xe4gsentwurf')
        self.assertIsNone(manager.get_checked_out_by())

    @browsing
    def test_not_possible_for_regular_user(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        # checkout
        browser.open(self.document)
        browser.click_on('Check out')
        assert_message(u'Checked out: Vertr\xe4gsentwurf')

        # force checkin as regular_user
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)

        with self.assertRaises(NoElementFound):
            browser.click_on('without comment')

        browser.open(self.document, view='@@checkin_without_comment')
        assert_message("This document is currently checked out by Ziegler Robert (robert.ziegler).")

        assert_message(u"Could not check in document Vertr\xe4gsentwurf")
