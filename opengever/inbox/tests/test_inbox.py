import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase


from opengever.inbox.tests.layer import Layer
from opengever.inbox.inbox import IInbox

class TestInboxIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.inbox.inbox', 'inbox1')
        i1 = self.folder['inbox1']
        self.failUnless(IInbox.providedBy(i1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.inbox.inbox')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.inbox.inbox')
        schema = fti.lookupSchema()
        self.assertEquals(IInbox, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.inbox.inbox')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IInbox.providedBy(new_object))

    def test_view(self):
        self.folder.invokeFactory('opengever.inbox.inbox', 'inbox1')
        i1 = self.folder['inbox1']
        view = i1.restrictedTraverse('@@view')
        self.failUnless(view())
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)