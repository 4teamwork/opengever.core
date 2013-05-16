from Products.CMFCore.utils import getToolByName
from opengever.base.interfaces import IRedirector
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from plone.app.testing import login, logout, setRoles, TEST_USER_NAME, TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from zope.component import getMultiAdapter
import datetime
import transaction


def obj2brain(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path': {'query': '/'.join(obj.getPhysicalPath()),
                      'depth': 0}}
    brains = catalog(query)
    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)
    else:
        return brains[0]

class TestCheckinCheckoutManager(FunctionalTestCase):

    def setUp(self):
        super(TestCheckinCheckoutManager, self).setUp()
        self.prepareSession()
        self.grant('Manager','Editor','Contributor')

        self.dossier = createContentInContainer(
            self.portal, 'opengever.dossier.businesscasedossier',
            title='Testdossier', checkConstraints=False)

        transaction.commit()

    def test_reverting(self):
        """Test that reverting to a version creates a new NamedBlobFile instance
        instead of using a reference.
        This avoids the version being reverted to being overwritte later.
        """
        portal = self.layer['portal']
        pr = getToolByName(portal, 'portal_repository')
        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Manager','Editor','Contributor'])
        file0 = NamedBlobFile('bla bla 0', filename=u'test.txt')
        file1 = NamedBlobFile('bla bla 1', filename=u'test.txt')
        file2 = NamedBlobFile('bla bla 2', filename=u'test.txt')
        file3 = NamedBlobFile('bla bla 2', filename=u'test.txt')
        doc1 = createContentInContainer(portal,
                                        'opengever.document.document',
                                        title=u'Some Doc',
                                        document_author=u'Hugo Boss',
                                        document_date=datetime.date(2011,1,1),
                                        file=file0)
        self.failUnless(IDocumentSchema.providedBy(doc1))
        manager = getMultiAdapter((doc1, portal.REQUEST), ICheckinCheckoutManager)

        manager.checkout()
        doc1.file = file1
        manager.checkin(comment="Created Version 1")

        manager.checkout()
        doc1.file = file2
        manager.checkin(comment="Created Version 2")

        manager.checkout()
        doc1.file = file3
        manager.checkin(comment="Created Version 3")

        manager.revert_to_version(2)
        version2 = pr.retrieve(doc1, 2)
        self.assertTrue(doc1.file._blob != version2.object.file._blob)
        self.assertTrue(doc1.file != version2.object.file)


    def test_checkout(self):
        # create a defaultfolder
        self.portal.invokeFactory('Folder', 'folder')

        folder = self.portal['folder']
        transaction.commit()
        pr = getToolByName(self.portal, 'portal_repository')

        # create a document, and get the CheckinCheckoutManager for the document
        mok_file1 = NamedBlobFile('bla bla', filename=u'test.txt')
        mok_file2 = NamedBlobFile('bla bla', filename=u'test.txt')
        doc1 = createContentInContainer(self.portal, 'opengever.document.document',
                                        title=u'Doc \xf6ne', document_author=u'Hugo Boss',
                                        document_date=datetime.date(2011,1,1), file=mok_file1)
        doc2 = createContentInContainer(self.portal, 'opengever.document.document',
                                        title=u"Doc two", file=mok_file2)
        doc3 = createContentInContainer(self.portal, 'opengever.document.document',
                                        title=u"Doc three", file=mok_file2)
        manager = getMultiAdapter((doc1, self.portal.REQUEST), ICheckinCheckoutManager)
        manager2 = getMultiAdapter((doc2, self.portal.REQUEST), ICheckinCheckoutManager)
        manager3 = getMultiAdapter((doc3, self.portal.REQUEST), ICheckinCheckoutManager)



        # Checkout:
        # checkout should now allowed, but just for a user with authorization

        self.assertTrue(manager.is_checkout_allowed())

        # the annotations should be still empty
        self.assertEquals(None, manager.checked_out())

        # checkout the document
        manager.checkout()
        self.assertEquals('test_user_1_', manager.checked_out())

        # cancelling and checkin should be allowed for the 'test_user_1_'
        self.assertTrue(manager.is_checkin_allowed())
        self.assertTrue(manager.is_cancel_allowed())

        self.assertFalse(manager.is_checkout_allowed())

        # Checkout when locked by another user:

        # Create a second user to test locking and checkout
        self.portal.acl_users.userFolderAddUser(
            'other_user', 'secret', ['Member'], [])

        # Checkout should first be allowed
        self.assertTrue(manager3.is_checkout_allowed())

        # Switch to different user and lock the document
        logout()
        login(self.portal, 'other_user')
        setRoles(self.portal, 'other_user', ['Manager','Editor','Contributor'])
        lockable = IRefreshableLockable(doc3)
        lockable.lock()

        # Log back in as the regular test user
        logout()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager','Editor','Contributor'])

        # Checkout should not be allowed since the document is locked by another user
        self.assertFalse(manager3.is_checkout_allowed())

        # checkin and cancelling:
        mok_file3 = NamedBlobFile('blubb blubb', filename=u"blubb.txt")
        doc1.file = mok_file3
        manager.checkin(comment="Test commit Nr. 1")

        transaction.commit()

        # document isn't checked out and the old object is in the history
        self.assertEquals(None, manager.checked_out())

        self.assertEquals(u'doc-one.txt',
                          pr.retrieve(doc1, 0).object.file.filename)
        self.assertEquals(u'blubb.txt', doc1.file.filename)

        manager.checkout()
        self.assertEquals('test_user_1_', manager.checked_out())

        manager.cancel()
        pr.getHistoryMetadata(doc1).retrieve(2)

        self.assertEquals(None, manager.checked_out())

        # Test the views:

        # editing_document:

        view = doc1.restrictedTraverse('@@editing_document')()

        # redirect to the document view, js-redirect to the external link
        self.assertEquals('http://nohost/plone/document-1', view)

        self.assertEquals('http://nohost/plone/document-1/external_edit',
                          IRedirector(doc1.REQUEST).get_redirects()[0].get('url'))


        # file is checked out
        self.assertEquals('test_user_1_', manager.checked_out())

        # cancel_document_checkouts:
        self.portal.REQUEST['paths'] = [obj2brain(doc1).getPath(),]
        view = doc1.restrictedTraverse('cancel_document_checkouts').render()
        self.assertEquals(None, manager.checked_out())

        # checkout_documents and a default-content-type:
        self.portal.REQUEST['paths'] = [
            obj2brain(doc1).getPath(),
            obj2brain(doc2).getPath(),
            obj2brain(folder).getPath()]
        view = doc1.restrictedTraverse('@@checkout_documents').render()
        self.assertEquals('test_user_1_', manager.checked_out())
        self.assertEquals('test_user_1_', manager2.checked_out())
