import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.repository.tests.layer import Layer

from opengever.repository.repositoryfolder import IRepositoryFolderSchema

class TestRepositoryFolderIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.repository.repositoryfolder', 'repository1')
        r1 = self.folder['repository1']
        self.failUnless(IRepositoryFolderSchema.providedBy(r1))    
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryfolder')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryfolder')
        schema = fti.lookupSchema()
        self.assertEquals(IRepositoryFolderSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryfolder')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IRepositoryFolderSchema.providedBy(new_object))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)