from datetime import timedelta
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.base.date_time import utcnow_tz_aware
from opengever.core.testing import MEMORY_DB_LAYER
from opengever.document.interfaces import IFileActions
from opengever.dossier.tests.test_move_items import MoveItemsHelper
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.locking.lock import MEETING_EXCERPT_LOCK
from opengever.locking.lock import MEETING_SUBMITTED_LOCK
from opengever.locking.model import Lock
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from opengever.trash.trash import ITrashed
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
from plone.protect import createToken
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
import json
import transaction


class TestUnitLocks(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitLocks, self).setUp()
        self.session = self.layer.session

    def test_valid_locks_query(self):
        valid = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=300))
        self.session.add(valid)

        invalid = Lock(object_type='Meeting',
                       object_id=2,
                       creator=TEST_USER_ID,
                       time=utcnow_tz_aware() - timedelta(seconds=800))
        self.session.add(invalid)

        query = Lock.query.valid_locks('Meeting', 1)
        self.assertEquals([valid], query.all())

    def test_is_valid(self):
        lock1 = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=300))
        self.session.add(lock1)

        lock2 = Lock(object_type='Meeting',
                     object_id=2,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=800))
        self.session.add(lock2)

        self.assertTrue(lock1.is_valid())
        self.assertFalse(lock2.is_valid())

    def test_unique_constraint_on_type_id_and_locktype(self):
        lock1 = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     lock_type=u'plone.locking.stealable',
                     time=utcnow_tz_aware() - timedelta(seconds=300))
        self.session.add(lock1)

        with self.assertRaises(IntegrityError):
            lock2 = Lock(object_type='Meeting',
                         object_id=1,
                         creator=TEST_USER_ID,
                         lock_type=u'plone.locking.stealable',
                         time=utcnow_tz_aware())
            self.session.add(lock2)
            transaction.commit()

        transaction.abort()


class TestDocumentsLockedWithMeetingSubmittedLock(SolrIntegrationTestCase, MoveItemsHelper):

    lock_type = MEETING_SUBMITTED_LOCK

    def test_no_checkout_or_edit_action_available_for_locked_document(self):
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)

        self.assertTrue(actions.is_any_checkout_or_edit_available())
        ILockable(self.document).lock(self.lock_type)
        self.assertFalse(actions.is_any_checkout_or_edit_available())

    def test_cannot_checkout_locked_document(self):
        self.login(self.regular_user)

        ILockable(self.document).lock(self.lock_type)
        with self.assertRaises(Unauthorized):
            self.checkout_document(self.document)

        ILockable(self.document).unlock(self.lock_type)
        self.checkout_document(self.document)

    @browsing
    def test_cannot_edit_metadata_of_locked_document(self, browser):
        self.login(self.regular_user, browser)

        ILockable(self.document).lock(self.lock_type)
        browser.open(self.document)
        self.assertIsNone(browser.find_link_by_text("Edit metadata"))

        # Opening the edit form redirects to the tabbed view
        browser.open(self.document, view='edit')
        self.assertEqual("{}/@@tabbed_view".format(self.document.absolute_url()), browser.url)

        ILockable(self.document).unlock(self.lock_type)
        browser.open(self.document)
        self.assertIsNotNone(browser.find_link_by_text("Edit metadata"))

        browser.open(self.document, view='edit')
        self.assertEqual("{}/edit".format(self.document.absolute_url()), browser.url)

    @browsing
    def test_cannot_patch_metadata_of_locked_document(self, browser):
        self.login(self.regular_user, browser)

        ILockable(self.document).lock(self.lock_type)
        with browser.expect_http_error(reason='Forbidden'):
            browser.open(
                self.document.absolute_url(),
                data='{"title": "New title"}',
                method='PATCH',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})

        self.assertEqual(u'Vertr\xe4gsentwurf', self.document.title)

        ILockable(self.document).unlock(self.lock_type)
        browser.open(
            self.document.absolute_url(),
            data='{"title": "New title"}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})

        self.assertEqual(u"New title", self.document.title)

    @browsing
    def test_action_menu_for_locked_document(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document)
        self.assertEqual(
            ['Check out', 'Copy item', 'Move item', 'Properties', 'Finalize'],
            editbar.menu_options('Actions'))

        ILockable(self.document).lock(self.lock_type)
        browser.open(self.document)
        self.assertEqual(['Copy item', 'Properties'],
                         editbar.menu_options('Actions'))

    @browsing
    def test_file_actions_for_locked_document_over_api(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)

        expected_file_actions = [
            u'oc_direct_checkout',
            u'download_copy',
            u'attach_to_email',
            u'trash_context',
            u'new_task_from_document']

        self.assertEqual(
            expected_file_actions,
            [action.get('id') for action in browser.json['file_actions']])

        ILockable(self.document).lock(self.lock_type)
        browser.open(self.document.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)

        expected_file_actions = [
            u'download_copy',
            u'attach_to_email',
            u'new_task_from_document',
            u'unlock']

        self.assertEqual(
            expected_file_actions,
            [action.get('id') for action in browser.json['file_actions']])

    def test_cannot_move_locked_document(self):
        self.login(self.manager)
        doc_title = self.document.title.encode("utf-8")
        self.assertIn(
            doc_title,
            [a.Title for a in self.dossier.getFolderContents()])
        self.assertNotIn(
            doc_title,
            [a.Title for a in self.empty_dossier.getFolderContents()])

        ILockable(self.document).lock(self.lock_type)
        self.move_items([self.document],
                        source=self.dossier,
                        target=self.empty_dossier)

        self.assertIn(
            doc_title,
            [a.Title for a in self.dossier.getFolderContents()])
        self.assertNotIn(
            doc_title,
            [a.Title for a in self.empty_dossier.getFolderContents()])

    @browsing
    def test_cannot_move_locked_document_over_api(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock(self.lock_type)
        doc_id = self.document.getId()

        with browser.expect_http_error(reason='Locked'):
            browser.open(
                self.subdossier.absolute_url() + '/@move',
                data=json.dumps({"source": self.document.absolute_url()}),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertEqual(423, browser.status_code)
        self.assertIn(doc_id, self.dossier)
        self.assertNotIn(doc_id, self.subdossier)

    @browsing
    def test_cannot_trash_locked_document(self, browser):
        self.login(self.regular_user, browser=browser)
        ILockable(self.document).lock(self.lock_type)

        data = self.make_path_param(self.document)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trash_content", data=data)

        self.assertEqual(
            [u"Could not move document Vertr\xe4gsentwurf to the trash: it's currently locked.".format(
                self.document.title)],
            error_messages())
        self.assertFalse(ITrashed.providedBy(self.document))
        self.assertFalse(obj2brain(self.document, unrestricted=True).trashed)

    @browsing
    def test_cannot_trash_locked_document_over_api(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock(self.lock_type)

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'Cannot trash a locked document',
             u'message': u'msg_trash_locked_doc'},
            browser.json)
        self.assertFalse(ITrashed.providedBy(self.document))


class TestDocumentsLockedWithMeetingExcerptLock(TestDocumentsLockedWithMeetingSubmittedLock):

    lock_type = MEETING_EXCERPT_LOCK


class TestDocumentsLockedWithCopiedToWorkspaceLock(TestDocumentsLockedWithMeetingSubmittedLock):

    features = ('workspace_client', )

    lock_type = COPIED_TO_WORKSPACE_LOCK

    def test_indexes_the_is_locked_by_copy_to_workspace_state(self):
        self.login(self.regular_user)

        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).lock(self.lock_type)

        self.commit_solr()
        self.assertTrue(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).unlock(self.lock_type)
        self.commit_solr()
        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

    def test_indexes_the_is_locked_by_copy_to_workspace_state_when_clearing_all_locks(self):
        self.login(self.regular_user)

        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).lock(self.lock_type)

        self.commit_solr()
        self.assertTrue(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).clear_locks()
        self.commit_solr()
        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

    def test_do_not_index_the_is_locked_by_copy_to_workspace_state_for_other_locktypes(self):
        self.login(self.regular_user)

        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).lock()

        self.commit_solr()
        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).unlock()
        self.commit_solr()
        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

    def test_do_not_index_the_is_locked_by_copy_to_workspace_state_if_workspace_client_is_deactivated(self):
        self.deactivate_feature('workspace_client')
        self.login(self.regular_user)

        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))

        ILockable(self.document).lock(self.lock_type)

        self.commit_solr()
        self.assertFalse(solr_data_for(self.document, 'is_locked_by_copy_to_workspace'))
