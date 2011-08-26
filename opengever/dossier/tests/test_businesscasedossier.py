import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING

from opengever.dossier.businesscase import IBusinessCaseDossier

class TestBusinessCaseDossierIntegration(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.dossier.businesscasedossier', 'dossier1')
        d1 = portal['dossier1']
        self.failUnless(IBusinessCaseDossier.providedBy(d1))
        del portal['dossier1']

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.businesscasedossier')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.businesscasedossier')
        schema = fti.lookupSchema()
        self.assertEquals(IBusinessCaseDossier, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.businesscasedossier')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IBusinessCaseDossier.providedBy(new_object))


    # XXX
    # Don't work yet because its not possible to access to the dependent vocabulary from opengever.octopus.tentacle
    # def test_view(self):
    #     self.folder.invokeFactory('opengever.dossier.businesscasedossier', 'dossier1')
    #     d1 = self.folder['dossier1']
    #     view = d1.restrictedTraverse('@@view')
    #     self.failUnless(view())
