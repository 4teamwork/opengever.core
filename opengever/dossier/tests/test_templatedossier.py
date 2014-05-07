from Testing.makerequest import makerequest
from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.templatedossier import ITemplateDossier
from opengever.dossier.templatedossier import REMOVED_COLUMNS
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import obj2brain
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


DOCUMENT_TAB = 'tabbedview_view-documents'
TRASH_TAB = 'tabbedview_view-trash'


class TestTemplateDossierListings(FunctionalTestCase):

    def setUp(self):
        super(TestTemplateDossierListings, self).setUp()
        self.grant('Manager')

        self.templatedossier = create(Builder('templatedossier'))
        self.dossier = create(Builder('dossier'))

    def test_receipt_delivery_and_subdossier_column_are_hidden_in_document_tab(self):
        view = self.templatedossier.unrestrictedTraverse(DOCUMENT_TAB)
        view.update()
        columns = [col.get('column') for col in view.columns]

        self.assertEquals(
            ['', 'sequence_number', 'Title',
             'document_author', 'document_date', 'checked_out'],
            columns)

    def test_receipt_delivery_and_subdossier_column_are_hidden_in_trash_tab(self):
        view = self.templatedossier.unrestrictedTraverse(TRASH_TAB)
        view.update()
        columns = [col.get('column') for col in view.columns]

        self.assertEquals(
            ['', 'sequence_number', 'Title', 'document_author', 'document_date'],
            columns)

    def test_enabled_actions_are_limited_in_document_tab(self):
        view = self.templatedossier.unrestrictedTraverse(DOCUMENT_TAB)
        self.assertEquals(['trashed', 'copy_items', 'zip_selected'],
                          view.enabled_actions)

    def test_document_tab_lists_only_documents_directly_beneath(self):
        subdossier = create(Builder('templatedossier')
                            .within(self.templatedossier))
        document_a = create(Builder('document').within(self.templatedossier))
        document_b = create(Builder('document')
                            .within(subdossier))

        view = self.templatedossier.unrestrictedTraverse(DOCUMENT_TAB)
        view.update()

        self.assertEquals([document_a],
                          [brain.getObject() for brain in view.contents])

    def test_trash_tab_lists_only_documents_directly_beneath(self):
        subdossier = create(Builder('templatedossier')
                            .within(self.templatedossier))
        document_a = create(Builder('document')
                            .trashed()
                            .within(self.templatedossier))
        document_b = create(Builder('document')
                            .trashed()
                            .within(subdossier))

        view = self.templatedossier.unrestrictedTraverse(TRASH_TAB)
        view.update()

        self.assertEquals(document_a,
                          [brain.getObject() for brain in view.contents])
