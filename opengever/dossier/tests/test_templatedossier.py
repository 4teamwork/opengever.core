import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING

from opengever.dossier.templatedossier import ITemplateDossier

class TestTemplateDossierIntegration(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.dossier.templatedossier', 'document1')
        d1 = portal['document1']
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

    # XXX
    # Don't work yet because its not possible to access to the dependent vocabulary from opengever.octopus.tentacle
    # def test_view(self):
    #     self.folder.invokeFactory('opengever.dossier.templatedossier', 'dossier1')
    #     d1 = self.folder['dossier1']
    #     view = d1.restrictedTraverse('@@view')
    #     self.failUnless(view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)