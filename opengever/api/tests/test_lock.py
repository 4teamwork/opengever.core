from ftw.testbrowser import browsing
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.locking.lock import LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import ILockable
import json


class TestLock(IntegrationTestCase):

    @browsing
    def test_lock_is_expandable(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '?expand=lock',
                     method='GET', headers=self.api_headers)
        self.assertEqual({
            u'stealable': True, u'locked': False,
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/document-14/@lock'
        }, browser.json['@components']['lock'])


class TestUnlock(IntegrationTestCase):

    @browsing
    def test_unlock_without_unlock_type(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        self.assertTrue(ILockable(self.document).locked())

        browser.open(self.document, view='/@unlock', method='POST', headers=self.api_headers)

        self.assertFalse(ILockable(self.document).locked())
        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'stealable': True, u'locked': False}, browser.json)

    @browsing
    def test_unlock_not_locked_document_does_not_raise_an_error(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='/@unlock', method='POST', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'stealable': True, u'locked': False}, browser.json)

    @browsing
    def test_unlock_with_invalid_lock_type_does_not_raise_an_error(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock(COPIED_TO_WORKSPACE_LOCK)
        browser.open(self.document, view='/@unlock',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({"lock_type": "invalid"}))
        self.assertEqual(200, browser.status_code)
        self.assertTrue(browser.json['locked'])

    @browsing
    def test_user_cannot_remove_lock_of_another_user(self, browser):
        self.login(self.dossier_responsible, browser)
        ILockable(self.document).lock()

        self.login(self.regular_user, browser)
        browser.open(self.document, view='/@unlock',
                     method='POST', headers=self.api_headers)

        self.assertTrue(ILockable(self.document).locked())
        self.assertEqual(200, browser.status_code)
        self.assertTrue(browser.json['locked'])
        self.assertEqual(self.dossier_responsible.getId(), browser.json['creator'])

    @browsing
    def test_user_can_remove_workspace_lock_of_another_user(self, browser):
        self.login(self.dossier_responsible, browser)
        ILockable(self.document).lock(COPIED_TO_WORKSPACE_LOCK)
        self.assertTrue(ILockable(self.document).locked())

        self.login(self.regular_user, browser)
        browser.open(self.document, view='/@unlock',
                     method='POST', headers=self.api_headers,
                     data=json.dumps({"lock_type": LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK}))
        self.assertFalse(ILockable(self.document).locked())
        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'stealable': True, u'locked': False}, browser.json)

    @browsing
    def test_manager_can_remove_lock_of_another_user(self, browser):
        self.login(self.dossier_responsible, browser)
        ILockable(self.document).lock()

        self.login(self.manager, browser)
        browser.open(self.document, view='/@unlock',
                     method='POST', headers=self.api_headers)

        self.assertFalse(ILockable(self.document).locked())
        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'stealable': True, u'locked': False}, browser.json)
