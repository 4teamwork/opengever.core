import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.dossier.tests.layer import Layer

from opengever.dossier.templatedossier import ITemplateDossier

class TestTemplateDossierIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.dossier.templatedossier', 'document1')
        d1 = self.folder['document1']
        self.failUnless(ITemplateDossier.providedBy(d1))    
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.templatedossier')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.templatedossier')
        schema = fti.lookupSchema()
        self.assertEquals(ITemplateDossier, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.templatedossier')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(ITemplateDossier.providedBy(new_object))

    def test_view(self):
        self.folder.invokeFactory('opengever.dossier.templatedossier', 'dossier1')
        d1 = self.folder['dossier1']
        view = d1.restrictedTraverse('@@view')
        self.failUnless(view())
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)