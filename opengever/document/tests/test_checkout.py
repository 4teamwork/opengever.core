from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING
from plone.app.testing import login, setRoles, TEST_USER_NAME, TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import datetime
import unittest2 as unittest


class TestCheckinCheckoutManager(unittest.TestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
