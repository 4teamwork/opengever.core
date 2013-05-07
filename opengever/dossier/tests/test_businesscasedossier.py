from opengever.dossier.businesscase import IBusinessCaseDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_FUNCTIONAL_TESTING
from opengever.testing import FunctionalTestCase
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from zope.component import createObject
from zope.component import queryUtility


class TestBusinessCaseDossierIntegration(FunctionalTestCase):

    layer = OPENGEVER_DOSSIER_FUNCTIONAL_TESTING

    def test_adding(self):
        self.grant('Contributor')

        portal = self.layer['portal']
        portal.invokeFactory('opengever.dossier.businesscasedossier', 'dossier1')
        d1 = portal['dossier1']
        self.failUnless(IBusinessCaseDossier.providedBy(d1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.businesscasedossier')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.dossier.businesscasedossier')
        schema = fti.lookupSchema()
        self.assertEquals(IBusinessCaseDossier, schema)

    def test_factory(self):
        self.grant('Contributor')

        fti = queryUtility(IDexterityFTI, name='opengever.dossier.businesscasedossier')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IBusinessCaseDossier.providedBy(new_object))

    def test_accessors(self):
        """Test title and descprition accessors."""
        self.grant('Contributor')

        portal = self.layer['portal']
        d1 = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier',
            title=u'Test title', description=u'Lorem ipsum')
        self.assertEquals(d1.Title(), 'Test title')
        self.assertEquals(d1.Description(), 'Lorem ipsum')
