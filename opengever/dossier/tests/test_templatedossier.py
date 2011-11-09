from Testing.makerequest import makerequest
from opengever.dossier.templatedossier import ITemplateDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from zope.app.component.hooks import setSite
from zope.component import createObject, queryUtility
import transaction
import unittest2 as unittest


class TestTemplateDossierIntegration(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.dossier.templatedossier', 'templatedossier')
        d1 = portal['templatedossier']
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

    def test_templatefolder_view(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, [
                'Manager', 'Reader', 'Member', 'Contributor', 'Editor'])
        portal = makerequest(portal)
        setSite(portal)
        templates = createContentInContainer(portal, 'opengever.dossier.templatedossier', title="templates")
        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', title="dossier")
        dossier = makerequest(dossier)

        createContentInContainer(
            templates, 'opengever.document.document', title="empty document template")

        dossier.REQUEST['ACTUAL_URL'] = dossier.absolute_url()
        templates.reindexObject()
        transaction.commit()
        view = dossier.restrictedTraverse('document_with_template')
        self.failUnless(view())
        self.assertTrue('empty document template', view.templates())
