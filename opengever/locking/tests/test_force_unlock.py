from ftw.testbrowser import browsing
from plone.locking.interfaces import ILockable
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.officeconnector.testing import OCIntegrationTestCase
from ftw.testing import freeze


class TestDocumentForceUnlock(OCIntegrationTestCase):

    features = ('officeconnector-checkout',)

    locked_message = u'This item was locked by B\xe4rfuss K\xe4thi 1 minute ago.'
    unlockable_message = u'This item was locked by B\xe4rfuss K\xe4thi 1 minute ago.'\
                         ' If you are certain this user has abandoned the object,'\
                         ' you may the object. You will then be able to edit it.'

    @browsing
    def test_unlock_button_available_only_for_managers(self, browser):
        with freeze():
            self.login(self.regular_user, browser)
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
            tokens = self.validate_checkout_token(self.regular_user, oc_url, self.document)
            self.lock_document(browser, tokens, self.document)

            self.login(self.meeting_user, browser)
            browser.open(self.document)
            self.assertIn(self.locked_message, info_messages())
            self.assertNotIn(self.unlockable_message, info_messages())

            self.login(self.manager, browser)
            browser.open(self.document)
            self.assertNotIn(self.locked_message, info_messages())
            self.assertIn(self.unlockable_message, info_messages())

    @browsing
    def test_force_unlock_clears_lock(self, browser):
        self.login(self.regular_user, browser)
        oc_url = self.fetch_document_checkout_oc_url(browser, self.document)
        tokens = self.validate_checkout_token(self.regular_user, oc_url, self.document)
        lockable = ILockable(self.document)

        self.lock_document(browser, tokens, self.document)
        self.assertTrue(lockable.locked())

        self.login(self.manager, browser)
        browser.open(self.document)
        browser.click_on("Unlock")
        self.assertFalse(lockable.locked())
