import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.base.tests.layer import Layer

from opengever.base.workspace import IWorkspace

class TestWorkspaceIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.base.workspace', 'ws1')
        w1 = self.folder['ws1']
        self.failUnless(IWorkspace.providedBy(w1))    
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.base.workspace')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.base.workspace')
        schema = fti.lookupSchema()
        self.assertEquals(IWorkspace, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.base.workspace')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IWorkspace.providedBy(new_object))
        
    def test_view(self):
        self.folder.invokeFactory('opengever.base.workspace', 'ws1')
        w1 = self.folder['ws1']
        w1.keywords=()
        view = w1.restrictedTraverse('@@tabbed_view')
        # collective.js.jqueryui compatibility:
        self.portal.REQUEST.LANGUAGE = 'de'
        self.failUnless(view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
