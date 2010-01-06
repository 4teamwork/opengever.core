import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.document.tests.layer import Layer

from opengever.document.document import IDocumentSchema

class TestDocumentIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.document.document', 'document1')
        d1 = self.folder['document1']
        self.failUnless(IDocumentSchema.providedBy(d1))    
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        schema = fti.lookupSchema()
        self.assertEquals(IDocumentSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDocumentSchema.providedBy(new_object))
        
    def test_view(self):
        self.folder.invokeFactory('opengever.document.document', 'document1')
        d1 = self.folder['document1']
        d1.keywords=()
        view = d1.restrictedTraverse('@@view')
        self.failUnless(view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)