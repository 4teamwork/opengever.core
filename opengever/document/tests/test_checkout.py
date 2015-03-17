from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.interfaces import IRedirector
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from plone.protect import createToken
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import datetime
import transaction


class TestCheckinCheckoutManager(FunctionalTestCase):

    def setUp(self):
        super(TestCheckinCheckoutManager, self).setUp()
        self.prepareSession()
        self.grant('Manager', 'Editor', 'Contributor')

    def test_reverting(self):
        """Test that reverting to a version creates a new NamedBlobFile instance
        instead of using a reference.
        This avoids the version being reverted to being overwritte later.
        """
        pr = getToolByName(self.portal, 'portal_repository')
        doc1 = createContentInContainer(self.portal,
                                        'opengever.document.document',
                                        title=u'Some Doc',
                                        document_author=u'Hugo Boss',
                                        document_date=datetime.date(2011, 1, 1),
                                        file=NamedBlobFile('bla bla 0',
                                                           filename=u'test.txt'))
        manager = self.get_manager(doc1)

        manager.checkout()
        doc1.file = NamedBlobFile('bla bla 1', filename=u'test.txt')
        manager.checkin(comment="Created Version 1")

        manager.checkout()
        doc1.file = NamedBlobFile('bla bla 2', filename=u'test.txt')
        manager.checkin(comment="Created Version 2")

        manager.checkout()
        doc1.file = NamedBlobFile('bla bla 3', filename=u'test.txt')
        manager.checkin(comment="Created Version 3")

        manager.revert_to_version(2)

        version2 = pr.retrieve(doc1, 2)
        self.assertTrue(doc1.file._blob != version2.object.file._blob)
        self.assertTrue(doc1.file != version2.object.file)

    def test_checkout(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u'Doc \xf6ne', document_author=u'Hugo Boss',
            document_date=datetime.date(2011, 1, 1),
            file=NamedBlobFile('bla bla', filename=u'test.txt'))

        transaction.commit()

        view = doc1.restrictedTraverse('@@editing_document')()

        self.assertEquals('http://nohost/plone/document-1', view)
        self.assertEquals('http://nohost/plone/document-1/external_edit',
                          IRedirector(doc1.REQUEST).get_redirects()[0].get('url'))
        self.assertEquals(TEST_USER_ID, self.get_manager(doc1).get_checked_out_by())

    def test_cancel(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u'Doc \xf6ne', document_author=u'Hugo Boss',
            document_date=datetime.date(2011, 1, 1),
            file=NamedBlobFile('bla bla', filename=u'test.txt'))

        manager = self.get_manager(doc1)
        manager.checkout()

        transaction.commit()
        self.portal.REQUEST['paths'] = [obj2brain(doc1).getPath(),]
        view = doc1.restrictedTraverse('cancel_document_checkouts')()

        self.assertEquals('http://nohost/plone/document-1', view)
        self.assertEquals(None, manager.get_checked_out_by())

    def test_bulk_checkout(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u'Document1', document_author=u'Hugo Boss',
            document_date=datetime.date(2011, 1, 1),
            file=NamedBlobFile('bla bla', filename=u'test.txt'))
        doc2 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u'Document2', document_author=u'Hugo Boss',
            document_date=datetime.date(2011, 1, 1),
            file=NamedBlobFile('bla bla', filename=u'test.txt'))

        self.portal.REQUEST['paths'] = [
            obj2brain(doc1).getPath(),
            obj2brain(doc2).getPath(),
        ]
        view = self.portal.restrictedTraverse(
            '@@checkout_documents').render()
        self.assertEquals('http://nohost/plone#documents', view)

        self.assertEquals(TEST_USER_ID, self.get_manager(doc1).get_checked_out_by())
        self.assertEquals(TEST_USER_ID, self.get_manager(doc2).get_checked_out_by())

    def test_bluk_checkout_ignores_non_documents(self):
        self.skipTest("Needs to be implemented")

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)


class TestCheckinViews(FunctionalTestCase):
    def setUp(self):
        super(TestCheckinViews, self).setUp()

        self.dossier = create(Builder("dossier"))
        self.document = create(Builder("document")
                               .checked_out_by(TEST_USER_ID)
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
                           .checked_out_by(TEST_USER_ID)
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



# TODO: rewrite this test-case to express intent
class TestCheckinCheckoutManagerAPI(FunctionalTestCase):
    def setUp(self):
        super(TestCheckinCheckoutManagerAPI, self).setUp()
        self.grant('Manager','Editor','Contributor')

    def test_api(self):
        # create a defaultfolder
        pr = getToolByName(self.portal, 'portal_repository')

        # create a document, and get the CheckinCheckoutManager for the document
        mok_file1 = NamedBlobFile('bla bla', filename=u'test.txt')
        mok_file2 = NamedBlobFile('bla bla', filename=u'test.txt')
        doc1 = createContentInContainer(self.portal, 'opengever.document.document',
                                        title=u'Doc \xf6ne', document_author=u'Hugo Boss',
                                        document_date=datetime.date(2011,1,1), file=mok_file1)
        doc2 = createContentInContainer(self.portal, 'opengever.document.document',
                                        title=u"Doc three", file=mok_file2)
        manager = getMultiAdapter((doc1, self.portal.REQUEST), ICheckinCheckoutManager)
        manager2 = getMultiAdapter((doc2, self.portal.REQUEST), ICheckinCheckoutManager)

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
        lockable = IRefreshableLockable(doc2)
        lockable.lock()

        # Log back in as the regular test user
        logout()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager','Editor','Contributor'])

        # Checkout should not be allowed since the document is locked by another user
        self.assertFalse(manager2.is_checkout_allowed())

        # checkin and cancelling:
        mok_file2 = NamedBlobFile('blubb blubb', filename=u"blubb.txt")
        doc1.file = mok_file2
        manager.checkin(comment="Test commit Nr. 1")

        transaction.commit()

        # document isn't checked out and the old object is in the history
        self.assertIsNone(manager.get_checked_out_by())

        self.assertEquals(u'doc-one.txt',
                          pr.retrieve(doc1, 0).object.file.filename)
        self.assertEquals(u'blubb.txt', doc1.file.filename)

        manager.checkout()
        self.assertEquals('test_user_1_', manager.get_checked_out_by())

        manager.cancel()
        pr.getHistoryMetadata(doc1).retrieve(2)

        self.assertIsNone(manager.get_checked_out_by())
