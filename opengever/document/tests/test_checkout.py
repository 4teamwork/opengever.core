from Products.CMFCore.utils import getToolByName
from Products.Five.testbrowser import Browser
from Testing import makerequest
from opengever.base.interfaces import IRedirector
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING
from opengever.testing import FunctionalTestCase
from plone.app.testing import login, logout, setRoles, TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login, setRoles, TEST_USER_NAME, TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from zope.component import getMultiAdapter
from zope.component import getUtility
import datetime
import unittest2 as unittest


class TestCheckinCheckoutManager(FunctionalTestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

    def setUp(self):
        self.grant('Manager','Editor','Contributor')

        self.dossier = createContentInContainer(
            self.portal, 'opengever.dossier.businesscasedossier',
            title='Testdossier', checkConstraints=False)

        portal = makerequest.makerequest(portal)

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


    # def test_checkout(self):
    #     # create a document, and get the CheckinCheckoutManager for the document

    #     mok_file1 = NamedBlobFile('bla bla', filename=u'test.txt')
    #     mok_file2 = NamedBlobFile('bla bla', filename=u'test.txt')
    #     doc1 = createContentInContainer(portal, 'opengever.document.document',
    #                          title=u'Doc \xf6ne', document_author=u'Hugo Boss',
    #                          document_date=datetime.date(2011,1,1), file=mok_file1)
    #     doc2 = createContentInContainer(portal, 'opengever.document.document',
    #                          title=u"Doc two", file=mok_file2)
    #     doc3 = createContentInContainer(portal, 'opengever.document.document',
    #                          title=u"Doc three", file=mok_file2)
    #     manager = getMultiAdapter((doc1, portal.REQUEST), ICheckinCheckoutManager)
    #     manager2 = getMultiAdapter((doc2, portal.REQUEST), ICheckinCheckoutManager)
    #     manager3 = getMultiAdapter((doc3, portal.REQUEST), ICheckinCheckoutManager)

    def test_checkout(self):
        doc = self.create_document()
        manager = getMultiAdapter(
            (doc, portal.REQUEST), ICheckinCheckoutManager)

        self.assertTrue(manager.is_checkout_allowed(),)
        self.assertEquals(None, manager.checked_out())

        manager.checkout()
        self.assertEquals(TEST_USER_ID, manager.checked_out())

        self.assertTrue(manager.is_checkin_allowed())
        self.assertTrue(manager.is_cancel_allowed())
        self.assertFalse(manager.is_checkout_allowed())

    def test_checkout_when_locked_by_another_user(self):
        doc = self.create_document()
        manager = getMultiAdapter(
            (doc, portal.REQUEST), ICheckinCheckoutManager)

        # Create a second user to test locking and checkout
        self.portal.acl_users.userFolderAddUser(
            'other_user', 'secret', ['Member'], [])

        # Checkout should first be allowed
        manager3.is_checkout_allowed()
        #     True

        # Switch to different user and lock the document
        logout()
        login(portal, 'other_user')
        setRoles(portal, 'other_user', ['Manager','Editor','Contributor'])
        lockable = IRefreshableLockable(doc3)
        lockable.lock()

        # Log back in as the regular test user
        logout()
        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Manager','Editor','Contributor'])

        # Checkout should not be allowed since the document is locked by another user
        manager3.is_checkout_allowed()
        #     False


    def obj2brain(obj):
        catalog = getToolByName(obj, 'portal_catalog')
        query = {'path': {'query': '/'.join(obj.getPhysicalPath()),
                          'depth': 0}}
        brains = catalog(query)
        if len(brains) == 0:
            raise Exception('Not in catalog: %s' % obj)
        else:
            return brains[0]

    def create_document(self):
        _file  = NamedBlobFile('bla bla', filename=u'test.txt')
        doc1 = createContentInContainer(
            portal, 'opengever.document.document',
            title=u'Doc \xf6ne', document_author=u'Hugo Boss',
            document_date=datetime.date(2011,1,1), file=_file)
