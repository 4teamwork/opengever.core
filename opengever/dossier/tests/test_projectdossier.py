import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.dossier.tests.layer import Layer

from opengever.dossier.project import IProjectDossier

class TestProjectDossierIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.dossier.projectdossier', 'dossier1')
        d1 = self.folder['dossier1']
        self.failUnless(IProjectDossier.providedBy(d1))    
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.projectdossier')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.projectdossier')
        schema = fti.lookupSchema()
        self.assertEquals(IProjectDossier, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.projectdossier')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IProjectDossier.providedBy(new_object))

    def test_view(self):
        self.folder.invokeFactory('opengever.dossier.projectdossier', 'dossier1')
        d1 = self.folder['dossier1']
        view = d1.restrictedTraverse('@@view')
        self.failUnless(view())
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)