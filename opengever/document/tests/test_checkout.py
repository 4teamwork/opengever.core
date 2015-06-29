from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.interfaces import IRedirector
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from plone.protect import createToken
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import transaction
import unittest


class TestCheckinCheckoutManager(FunctionalTestCase):

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

    def test_reverting(self):
        """Test that reverting to a version creates a new NamedBlobFile instance
        instead of using a reference.
        This avoids the version being reverted to being overwritte later.
        """
        pr = getToolByName(self.portal, 'portal_repository')
        manager = self.get_manager(self.doc1)

        manager.checkout()
        self.doc1.file = NamedBlobFile('bla bla 1', filename=u'test.txt')
        manager.checkin(comment="Created Version 1")

        manager.checkout()
        self.doc1.file = NamedBlobFile('bla bla 2', filename=u'test.txt')
        manager.checkin(comment="Created Version 2")

        manager.checkout()
        self.doc1.file = NamedBlobFile('bla bla 3', filename=u'test.txt')
        manager.checkin(comment="Created Version 3")

        manager.revert_to_version(2)

        version2 = pr.retrieve(self.doc1, 2)
        self.assertTrue(self.doc1.file._blob != version2.object.file._blob)
        self.assertTrue(self.doc1.file != version2.object.file)

    def test_checkout(self):
        view = self.doc1.restrictedTraverse('@@editing_document')()

        self.assertEquals(self.doc1.absolute_url(), view)
        self.assertEquals(
            self.doc1.absolute_url() + '/external_edit',
            IRedirector(self.doc1.REQUEST).get_redirects()[0].get('url'))
        self.assertEquals(TEST_USER_ID,
                          self.get_manager(self.doc1).get_checked_out_by())

    def test_cancel(self):
        manager = self.get_manager(self.doc1)
        manager.checkout()

        transaction.commit()
        self.portal.REQUEST['paths'] = [obj2brain(self.doc1).getPath(),]
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
        browser.fill({'Journal Comment Describe, why you checkin the selected documents': 'Checkinerino'})
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
        browser.fill({'Journal Comment Describe, why you checkin the selected documents': 'Checkini'})
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

    @unittest.skip("Switching to new implementation")
    @browsing
    def test_reverting_with_revert_link_in_history_viewlet(self, browser):
        document = create(Builder("document")
                          .checked_out_by(TEST_USER_ID)
                          .within(self.dossier))

        browser.login().open(document)
        browser.css('#checkin_without_comment').first.click()

        browser.css('a.function-revert')[-1].click()
        self.assertEquals(['Reverted file to version 0'], info_messages())


# TODO: rewrite this test-case to express intent
class TestCheckinCheckoutManagerAPI(FunctionalTestCase):

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

        # create a document, and get the CheckinCheckoutManager for the document
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
        setRoles(self.portal, 'other_user', ['Manager','Editor','Contributor'])
        lockable = IRefreshableLockable(self.doc2)
        lockable.lock()

        # Log back in as the regular test user
        logout()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager','Editor','Contributor'])

        # Checkout should not be allowed since the document is locked by another user
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
