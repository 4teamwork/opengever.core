from AccessControl import Unauthorized
from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.base.interfaces import IRedirector
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY  # noqa
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing.helpers import create_document_version
from opengever.trash.trash import Trasher
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from plone.protect import createToken
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter

import jwt
import transaction


class TestCheckin(FunctionalTestCase):
    """Tests for the checkin functionality."""

    def setUp(self):
        super(TestCheckin, self).setUp()
        self.dossier = create(Builder('dossier'))

        self.document = create(Builder('document')
                               .having(document_date=date(2014, 1, 1))
                               .within(self.dossier)
                               .checked_out())

        self.manager = self.get_manager(self.document)

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)

    def test_annotations_key_is_cleared(self):
        annotations = IAnnotations(self.document)
        self.assertEquals(
            TEST_USER_ID, annotations.get(CHECKIN_CHECKOUT_ANNOTATIONS_KEY))

        self.manager.checkin()

        self.assertEquals(
            None, annotations.get(CHECKIN_CHECKOUT_ANNOTATIONS_KEY))

    def test_new_version_is_created(self):
        self.manager.checkin()

        repo_tool = api.portal.get_tool('portal_repository')
        history = repo_tool.getHistory(self.document)
        self.assertEquals(2, len(history))

    def test_clear_locks(self):
        IRefreshableLockable(self.document).lock()
        self.assertTrue(IRefreshableLockable(self.document).locked())

        self.manager.checkin()
        self.assertFalse(IRefreshableLockable(self.document).locked())

    def test_document_date_is_updated_to_current_date(self):
        self.manager.checkin()

        self.assertEquals(date.today(), self.document.document_date)


class TestReverting(FunctionalTestCase):
    """Tests for reverting documents to older revisions."""

    def setUp(self):
        super(TestReverting, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .having(document_date=date(2014, 1, 1))
                               .within(self.dossier)
                               .attach_file_containing(
                                   u"INITIAL VERSION DATA", u"somefile.txt"))

        create_document_version(self.document, 1)
        create_document_version(self.document, 2)
        transaction.commit()

        self.manager = getMultiAdapter(
            (self.document, self.portal.REQUEST), ICheckinCheckoutManager)

    def test_creates_new_version_with_same_data(self):
        self.manager.revert_to_version(2)

        repo_tool = api.portal.get_tool('portal_repository')
        version2 = repo_tool.retrieve(self.document, 2)

        self.assertEquals(4, len(repo_tool.getHistory(self.document)))
        self.assertEqual(self.document.file.data, version2.object.file.data)
        self.assertEquals(u'Reverted file to version 2',
                          repo_tool.retrieve(self.document, 3).comment)

    def test_creates_a_new_blob_instance(self):
        self.manager.revert_to_version(2)

        repo_tool = api.portal.get_tool('portal_repository')
        version2 = repo_tool.retrieve(self.document, 2)

        self.assertNotEqual(
            self.document.file._blob, version2.object.file._blob)
        self.assertNotEqual(self.document.file, version2.object.file)

    def test_resets_document_date_to_reverted_version(self):
        with freeze(datetime(2015, 01, 28, 12, 00)):
            create_document_version(self.document, 3)

        self.document.document_date = date(2015, 5, 15)
        self.manager.revert_to_version(3)
        self.assertEquals(date(2015, 01, 28), self.document.document_date)

    def test_revert_disallowed_for_unprivileded_user(self):
        self.grant('Authenticated')
        self.assertFalse(self.manager.is_revert_allowed())

    def test_revert_disallowed_when_checked_out(self):
        self.manager.checkout()
        self.assertFalse(self.manager.is_revert_allowed())

    def test_revert_disallowed_when_locked(self):
        IRefreshableLockable(self.document).lock()
        self.assertFalse(self.manager.is_revert_allowed())

    def test_revert_disallowed_when_trashed(self):
        Trasher(self.document).trash()
        self.assertFalse(self.manager.is_revert_allowed())

    def test_manager_raises_unauthorized_when_reverting_disallowed(self):
        self.manager.checkout()

        with self.assertRaises(Unauthorized):
            self.manager.revert_to_version(2)

    @browsing
    def test_reverting_with_revert_link_in_versions_tab(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first

        second_row = listing.css('tr')[2]
        self.assertIn('This is Version 1', second_row.text)

        revert_link = second_row.css('td a')[-1]
        revert_link.click()

        self.assertEquals(['Reverted file to version 1'], info_messages())
        self.assertEquals('VERSION 1 DATA', self.document.file.data)

    @browsing
    def test_reset_link_discreet_when_reverting_disallowed(self, browser):
        self.manager.checkout()
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-versions')
        self.assertEqual('reset', browser.css('span.discreet').first.text)

    @browsing
    def test_browser_revert_view_raises_unauthorized_when_revert_disallowed(self, browser):  # noqa
        self.manager.checkout()
        transaction.commit()

        with self.assertRaises(Unauthorized):
            browser.login().open(self.document, view='revert-file-to-version',
                                 data={'version_id': 2,
                                       '_authenticator': createToken()})


class TestManagerHelpers(FunctionalTestCase):
    """Tests for the checkin-checkout manager helper functions."""

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)

    def test_is_checked_out_by_current_user(self):
        doc = create(Builder('document').checked_out())
        self.assertTrue(self.get_manager(doc).is_checked_out_by_current_user())

    def test_is_not_checked_out_by_current_user_when_document_is_checked_out_by_another_user(self):  # noqa
        doc = create(Builder('document').checked_out_by('hugo.boss'))
        self.assertFalse(
            self.get_manager(doc).is_checked_out_by_current_user())

    def test_is_not_checked_out_when_document_is_checked_in(self):
        doc = create(Builder('document'))
        self.assertFalse(
            self.get_manager(doc).is_checked_out_by_current_user())

    def test_file_upload_is_disallowed_when_document_is_locked(self):
        doc = create(Builder('document').checked_out())
        IRefreshableLockable(doc).lock()

        self.assertFalse(self.get_manager(doc).is_file_upload_allowed())

    def test_file_upload_is_disallowed_when_document_is_checked_out_by_other_user(self):  # noqa
        doc = create(Builder('document').checked_out_by('hugo.boss'))
        self.assertFalse(self.get_manager(doc).is_file_upload_allowed())

    def test_file_upload_is_disallowed_when_document_is_not_checked_out(self):
        doc = create(Builder('document'))
        self.assertFalse(self.get_manager(doc).is_file_upload_allowed())

    def test_file_upload_is_allowed_when_document_is_checked_out_and_not_locked(self):  # noqa
        doc = create(Builder('document').checked_out())
        self.assertTrue(self.get_manager(doc).is_file_upload_allowed())


class TestCheckinCheckoutManager(FunctionalTestCase):
    """Tests for the checkin-checkout manager."""

    def setUp(self):
        super(TestCheckinCheckoutManager, self).setUp()
        self.prepareSession()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.doc1 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .with_dummy_content())
        self.doc2 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document2')
            .with_dummy_content())

    def test_checkout(self):
        view = self.doc1.restrictedTraverse('@@editing_document')()

        self.assertEquals(self.doc1.absolute_url(), view)
        self.assertEquals(
            self.doc1.absolute_url() + '/external_edit',
            IRedirector(self.doc1.REQUEST).get_redirects()[0].get('url'))
        self.assertEquals(TEST_USER_ID,
                          self.get_manager(self.doc1).get_checked_out_by())

    @browsing
    def test_checkout_with_officeconnector_enabled(self, browser):
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        # We cannot freeze time due to the test browser being threaded
        oc_url = create_oc_url(
            self.doc1.REQUEST, self.doc1, {'action': 'checkout'})
        decoded_oc_url = jwt.decode(oc_url.split(':')[-1], verify=False)

        redirector_js = browser.login().open(
            self.doc1,
            view='checkout_documents'
            '?_authenticator={}&mode=external'
            .format(createToken()),
            ).css('script.redirector')[0].text

        tokens_from_js = [token for token in redirector_js.split("\'")
                          if 'oc:' in token]

        self.assertEqual(3, len(tokens_from_js))

        parsed_oc_url = tokens_from_js[0]
        decoded_parsed_oc_url = jwt.decode(
            parsed_oc_url.split(':')[-1], verify=False)

        # Take out the timestamps
        del decoded_oc_url['exp']
        del decoded_parsed_oc_url['exp']

        self.assertEqual(decoded_oc_url, decoded_parsed_oc_url)

    def test_cancel(self):
        manager = self.get_manager(self.doc1)
        manager.checkout()

        transaction.commit()
        self.portal.REQUEST['paths'] = [obj2brain(self.doc1).getPath(), ]
        view = self.doc1.restrictedTraverse('cancel_document_checkouts')()

        self.assertEquals(self.doc1.absolute_url(), view)
        self.assertEquals(None, manager.get_checked_out_by())

    def test_bulk_checkout(self):
        self.portal.REQUEST['paths'] = [
            obj2brain(self.doc1).getPath(),
            obj2brain(self.doc2).getPath(),
        ]
        view = self.portal.restrictedTraverse(
            '@@checkout_documents').render()
        self.assertEquals('http://nohost/plone#documents', view)

        self.assertEquals(
            TEST_USER_ID, self.get_manager(self.doc1).get_checked_out_by())
        self.assertEquals(
            TEST_USER_ID, self.get_manager(self.doc2).get_checked_out_by())

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)


class TestCheckinViews(FunctionalTestCase):
    """Tests for the checkin views."""

    def setUp(self):
        super(TestCheckinViews, self).setUp()

        self.dossier = create(Builder("dossier"))
        self.document = create(Builder("document")
                               .checked_out()
                               .within(self.dossier))

    @browsing
    def test_single_checkin_with_comment(self, browser):
        browser.login().open(self.document)

        # open checkin form
        browser.css('#checkin_with_comment').first.click()

        # fill and submit checkin form
        browser.fill({
            'Journal Comment Describe, why you checkin the selected documents':
            'Checkinerino'
            })
        browser.css('#form-buttons-button_checkin').first.click()

        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        self.assertEquals(None, manager.get_checked_out_by())

        # check last history entry to verify the checkin
        repository_tool = getToolByName(self.document, 'portal_repository')
        history = repository_tool.getHistory(self.document)
        last_entry = repository_tool.retrieve(self.document, len(history)-1)
        self.assertEquals('Checkinerino', last_entry.comment)

    @browsing
    def test_multi_checkin_from_tabbedview_with_comment(self, browser):
        document2 = create(Builder("document")
                           .checked_out()
                           .within(self.dossier))

        browser.login().open(
            self.dossier,
            data={'paths': [obj2brain(self.document).getPath(),
                            obj2brain(document2).getPath()],
                  'checkin_documents:method': 1,
                  '_authenticator': createToken()})

        # fill and submit checkin form
        browser.fill({
            'Journal Comment Describe, why you checkin the selected documents':
            'Checkini'
            })
        browser.css('#form-buttons-button_checkin').first.click()

        manager1 = getMultiAdapter((self.document, self.portal.REQUEST),
                                   ICheckinCheckoutManager)
        self.assertEquals(None, manager1.get_checked_out_by())
        manager2 = getMultiAdapter((document2, self.portal.REQUEST),
                                   ICheckinCheckoutManager)
        self.assertEquals(None, manager2.get_checked_out_by())

        # check last history entry to verify the checkin
        repository_tool = getToolByName(document2, 'portal_repository')
        history = repository_tool.getHistory(document2)
        last_entry = repository_tool.retrieve(document2, len(history)-1)
        self.assertEquals('Checkini', last_entry.comment)

    @browsing
    def test_single_checkin_without_comment(self, browser):
        browser.login().open(self.document)

        browser.css('#checkin_without_comment').first.click()

        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        self.assertEquals(None, manager.get_checked_out_by())

        # check last history entry to verify the checkin
        repository_tool = getToolByName(self.document, 'portal_repository')
        history = repository_tool.getHistory(self.document)
        last_entry = repository_tool.retrieve(self.document, len(history)-1)
        self.assertEquals(None, last_entry.comment)

    @browsing
    def test_multi_checkin_from_tabbedview_without_comment(self, browser):
        document2 = create(Builder("document")
                           .checked_out_by(TEST_USER_ID)
                           .within(self.dossier))

        browser.login().open(
            self.dossier,
            data={'paths': [obj2brain(self.document).getPath(),
                            obj2brain(document2).getPath()],
                  'checkin_without_comment:method': 1,
                  '_authenticator': createToken()})

        manager1 = getMultiAdapter((self.document, self.portal.REQUEST),
                                   ICheckinCheckoutManager)
        self.assertEquals(None, manager1.get_checked_out_by())
        manager2 = getMultiAdapter((document2, self.portal.REQUEST),
                                   ICheckinCheckoutManager)
        self.assertEquals(None, manager2.get_checked_out_by())

        # check last history entry to verify the checkin
        repository_tool = getToolByName(document2, 'portal_repository')
        history = repository_tool.getHistory(document2)
        last_entry = repository_tool.retrieve(document2, len(history)-1)
        self.assertEquals(None, last_entry.comment)

    @browsing
    def test_multi_checkin_shows_message_when_no_documents_are_selected(self, browser):  # noqa
        browser.login().open(
            self.dossier,
            data={'paths': [],
                  'checkin_without_comment:method': 1,
                  '_authenticator': createToken()})

        self.assertEquals(['You have not selected any documents'],
                          error_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)

        browser.login().open(
            self.dossier,
            data={'paths': [],
                  'checkin_documents:method': 1,
                  '_authenticator': createToken()})
        browser.click_on('Checkin')

        self.assertEquals(['You have not selected any documents'],
                          error_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)


# TODO: rewrite this test-case to express intent
class TestCheckinCheckoutManagerAPI(FunctionalTestCase):
    """Tests for the complete checkin-checkout cycle."""

    def setUp(self):
        super(TestCheckinCheckoutManagerAPI, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.doc1 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .with_dummy_content())
        self.doc2 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document2')
            .with_dummy_content())

    def test_api(self):
        # create a defaultfolder
        pr = getToolByName(self.portal, 'portal_repository')

        # create a document, and get CheckinCheckoutManager for the document
        manager = getMultiAdapter(
            (self.doc1, self.portal.REQUEST), ICheckinCheckoutManager)
        manager2 = getMultiAdapter(
            (self.doc2, self.portal.REQUEST), ICheckinCheckoutManager)

        # Checkout:
        # checkout should now allowed, but just for a user with authorization
        self.assertTrue(manager.is_checkout_allowed())

        # the annotations should be still empty
        self.assertIsNone(manager.get_checked_out_by())

        # checkout the document
        manager.checkout()
        self.assertEquals('test_user_1_', manager.get_checked_out_by())

        # cancelling and checkin should be allowed for the 'test_user_1_'
        self.assertTrue(manager.is_checkin_allowed())
        self.assertTrue(manager.is_cancel_allowed())

        self.assertFalse(manager.is_checkout_allowed())

        # Checkout when locked by another user:

        # Create a second user to test locking and checkout
        self.portal.acl_users.userFolderAddUser(
            'other_user', 'secret', ['Member'], [])

        # Checkout should first be allowed
        self.assertTrue(manager2.is_checkout_allowed())

        # Switch to different user and lock the document
        logout()
        login(self.portal, 'other_user')
        setRoles(
            self.portal, 'other_user', ['Manager', 'Editor', 'Contributor'])
        lockable = IRefreshableLockable(self.doc2)
        lockable.lock()

        # Log back in as the regular test user
        logout()
        login(self.portal, TEST_USER_NAME)
        setRoles(
            self.portal, TEST_USER_ID, ['Manager', 'Editor', 'Contributor'])

        # Checkout should not be allowed since the document is already
        # locked by an another user
        self.assertFalse(manager2.is_checkout_allowed())

        # checkin and cancelling:
        mok_file2 = NamedBlobFile('blubb blubb', filename=u"blubb.txt")
        self.doc1.file = mok_file2
        manager.checkin(comment="Test commit Nr. 1")

        transaction.commit()

        # document isn't checked out and the old object is in the history
        self.assertIsNone(manager.get_checked_out_by())

        self.assertEquals(u'document1.doc',
                          pr.retrieve(self.doc1, 0).object.file.filename)
        self.assertEquals(u'blubb.txt', self.doc1.file.filename)

        manager.checkout()
        self.assertEquals('test_user_1_', manager.get_checked_out_by())

        manager.cancel()
        pr.getHistoryMetadata(self.doc1).retrieve(2)

        self.assertIsNone(manager.get_checked_out_by())
