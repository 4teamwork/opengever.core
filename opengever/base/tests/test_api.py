from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.wopi.lock import create_lock as create_wopi_lock
from plone.locking.interfaces import ILockable
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestDocumentStatus(IntegrationTestCase):

    @browsing
    def test_document_status_for_mails(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.mail_eml, view='status', headers=self.api_headers)
        expected = {
            u'checked_out': False,
            u'checked_out_by': None,
            u'checked_out_collaboratively': False,
            u'int_id': getUtility(IIntIds).getId(self.mail_eml),
            u'locked': False,
            u'locked_by': None,
            u'title': u'Die B\xfcrgschaft',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_documents(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='status', headers=self.api_headers)

        expected = {
            u'checked_out': False,
            u'checked_out_by': None,
            u'checked_out_collaboratively': False,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'locked': False,
            u'locked_by': None,
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_checked_out_document(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        browser.open(self.document, view='status', headers=self.api_headers)

        expected = {
            u'checked_out': True,
            u'checked_out_by': self.regular_user.getId(),
            u'checked_out_collaboratively': False,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'locked': False,
            u'locked_by': None,
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_checked_out_and_locked_document(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        ILockable(self.document).lock()

        browser.open(self.document, view='status', headers=self.api_headers)

        expected = {
            u'checked_out': True,
            u'checked_out_by': self.regular_user.getId(),
            u'checked_out_collaboratively': False,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'locked': True,
            u'locked_by': self.regular_user.getId(),
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_collaboratively_checked_out_and_locked_document(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout(collaborative=True)
        create_wopi_lock(self.document, 'my-token')

        browser.open(self.document, view='status', headers=self.api_headers)

        expected = {
            u'checked_out': True,
            u'checked_out_by': self.regular_user.getId(),
            u'checked_out_collaboratively': True,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'locked': True,
            u'locked_by': self.regular_user.getId(),
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)

