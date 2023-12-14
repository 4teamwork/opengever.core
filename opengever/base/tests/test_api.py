from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing.freezer import freeze
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
            u'bumblebee_checksum': u'65da667b7c265f5aff1068c5216a3cba271fe57d3130ef152221661a45490d66',
            u'checked_out': False,
            u'checked_out_by': None,
            u'checked_out_collaboratively': False,
            u'checkout_collaborators': [],
            u'file_mtime': self.mail_eml.message._p_mtime,
            u'int_id': getUtility(IIntIds).getId(self.mail_eml),
            u'lock_time': None,
            u'lock_timeout': None,
            u'locked': False,
            u'locked_by': None,
            u'review_state': 'mail-state-active',
            u'title': u'Die B\xfcrgschaft',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_documents(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='status', headers=self.api_headers)
        expected = {
            u'bumblebee_checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
            u'checked_out': False,
            u'checked_out_by': None,
            u'checked_out_collaboratively': False,
            u'checkout_collaborators': [],
            u'file_mtime': self.document.file._p_mtime,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'lock_time': None,
            u'lock_timeout': None,
            u'locked': False,
            u'locked_by': None,
            u'review_state': 'document-state-draft',
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
            u'bumblebee_checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
            u'checked_out': True,
            u'checked_out_by': self.regular_user.getId(),
            u'checked_out_collaboratively': False,
            u'checkout_collaborators': [],
            u'file_mtime': self.document.file._p_mtime,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'lock_time': None,
            u'lock_timeout': None,
            u'locked': False,
            u'locked_by': None,
            u'review_state': 'document-state-draft',
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_checked_out_and_locked_document(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        with freeze(datetime(2021, 9, 6, 10, 54, 21)):
            ILockable(self.document).lock()
            browser.open(self.document, view='status', headers=self.api_headers)

        expected = {
            u'bumblebee_checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
            u'checked_out': True,
            u'checked_out_by': self.regular_user.getId(),
            u'checked_out_collaboratively': False,
            u'checkout_collaborators': [],
            u'file_mtime': self.document.file._p_mtime,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'lock_time': 1630918461.0,
            u'lock_timeout': 600,
            u'locked': True,
            u'locked_by': self.regular_user.getId(),
            u'review_state': 'document-state-draft',
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_document_status_for_collaboratively_checked_out_and_locked_document(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout(collaborative=True)
        with freeze(datetime(2021, 9, 6, 10, 54, 21)):
            create_wopi_lock(self.document, 'my-token')
            browser.open(self.document, view='status', headers=self.api_headers)

        expected = {
            u'bumblebee_checksum': '51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2',
            u'checked_out': True,
            u'checked_out_by': self.regular_user.id,
            u'checked_out_collaboratively': True,
            u'checkout_collaborators': [self.regular_user.id],
            u'file_mtime': self.document.file._p_mtime,
            u'int_id': getUtility(IIntIds).getId(self.document),
            u'lock_time': 1630918461.0,
            u'lock_timeout': 1800,
            u'locked': True,
            u'locked_by': self.regular_user.id,
            u'review_state': 'document-state-draft',
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected, browser.json)
