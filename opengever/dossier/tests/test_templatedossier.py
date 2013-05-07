from Testing.makerequest import makerequest
from opengever.dossier.templatedossier import ITemplateDossier
from opengever.dossier.templatedossier import REMOVED_COLUMNS
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from zope.app.component.hooks import setSite
from zope.component import createObject, queryUtility
import transaction


class TestTemplateDossierIntegration(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        self.grant('Contributor')
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
        self.grant('Manager', 'Reader', 'Member', 'Contributor', 'Editor')

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

        # test_tabbedview_columns
        view = templates.unrestrictedTraverse('tabbedview_view-documents')
        for column in view.columns:
            if isinstance(column, dict):
                self.assertTrue(column.get('id') not in REMOVED_COLUMNS)

        view = templates.unrestrictedTraverse('tabbedview_view-trash')
        for column in view.columns:
            if isinstance(column, dict):
                self.assertTrue(column.get('id') not in REMOVED_COLUMNS)
