from opengever.dossier.templatedossier import ITemplateDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject, queryUtility
import unittest2 as unittest


class TestTemplateDossierIntegration(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.dossier.templatedossier', 'document1')
        d1 = portal['document1']
        self.failUnless(ITemplateDossier.providedBy(d1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='opengever.dossier.templatedossier')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='opengever.dossier.templatedossier')
        schema = fti.lookupSchema()
        self.assertEquals(ITemplateDossier, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='opengever.dossier.templatedossier')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(ITemplateDossier.providedBy(new_object))

    def test_templatefolder_utility(self):

        pass
