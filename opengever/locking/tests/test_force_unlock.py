from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
from plone.locking.interfaces import ILockable
import jwt


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
            with freeze(datetime(2100, 8, 3, 15, 25)):
                oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

            expected_token = {
                u'action': u'checkout',
                u'documents': [u'createtreatydossiers000000000002'],
                u'exp': 4121033100,
                u'sub': u'kathi.barfuss',
                u'url': u'http://nohost/plone/oc_checkout',
                }
            raw_token = oc_url.split(':')[-1]
            token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
            self.assertEqual(token, expected_token)

            self.lock_document(browser, raw_token, self.document)

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
        with freeze(datetime(2100, 8, 3, 15, 25)):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.document)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'kathi.barfuss',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(token, expected_token)

        lockable = ILockable(self.document)
        self.lock_document(browser, raw_token, self.document)
        self.assertTrue(lockable.locked())

        self.login(self.manager, browser)
        browser.open(self.document)
        browser.click_on("Unlock")
        self.assertFalse(lockable.locked())
