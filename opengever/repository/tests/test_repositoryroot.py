import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.repository.tests.layer import Layer

from opengever.repository.repositoryroot import IRepositoryRoot

class TestRepositoryRootIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.repository.repositoryroot', 'repository1')
        r1 = self.folder['repository1']
        self.failUnless(IRepositoryRoot.providedBy(r1))    
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryroot')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryroot')
        schema = fti.lookupSchema()
        self.assertEquals(IRepositoryRoot, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryroot')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IRepositoryRoot.providedBy(new_object))
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)