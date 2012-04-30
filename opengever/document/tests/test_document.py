from datetime import date
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.testing import OPENGEVER_DOCUMENT_INTEGRATION_TESTING
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from z3c.form.interfaces import IValue
from zope.component import createObject
from zope.component import queryMultiAdapter, getAdapter
from zope.component import queryUtility, getUtility
from zope.interface import Invalid
from zope.schema import getFields
import unittest2 as unittest


class TestDocumentIntegration(unittest.TestCase):

    layer = OPENGEVER_DOCUMENT_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.document.document', 'document1')
        d1 = portal['document1']
        self.failUnless(IDocumentSchema.providedBy(d1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        schema = fti.lookupSchema()
        self.assertEquals(IDocumentSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDocumentSchema.providedBy(new_object))

    def test_upload_file(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.document.document', 'document1')
        d1 = portal['document1']
        field = IDocumentSchema['file']
        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        field.set(d1, monk_file)
        self.assertTrue(field.get(d1).data == 'bla bla')

    def test_digitally_available(self):
        portal = self.layer['portal']
        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        d1 = createContentInContainer(portal, 'opengever.document.document',
            file=monk_file)
        self.assertTrue(d1.digitally_available == True)
        d2 = createContentInContainer(portal, 'opengever.document.document')
        self.assertTrue(d2.digitally_available == False)

        # check the file_or_preserved_as_paper validator
        d3 = createContentInContainer(portal, 'opengever.document.document',
                checkConstraints=True, preserved_as_paper=False)
        try:
            IDocumentSchema.validateInvariants(d3)
            self.fail()
        except Invalid:
            pass

    def test_views(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.document.document', 'document1')
        d1 = portal['document1']
        d1.keywords = ()

        # fake the request
        portal.REQUEST['ACTUAL_URL'] = d1.absolute_url()

        view = d1.restrictedTraverse('@@view')
        self.failUnless(view())
        tabbed_view = d1.restrictedTraverse('@@tabbed_view')
        self.failUnless(tabbed_view())

    def test_copying(self):
        portal = self.layer['portal']
        portal.invokeFactory(
            'opengever.document.document',
            'document1', title="Testdocument")
        d1 = portal['document1']

        cb = portal.manage_copyObjects(d1.id)
        portal.manage_pasteObjects(cb)
        self.assertTrue(
            portal['copy_of_document1'].title == u'copy of Testdocument')

    def test_copying_and_versions(self):
        portal = self.layer['portal']
        pr = portal.portal_repository
        orig_doc = createContentInContainer(
            portal,
            'opengever.document.document',
            checkConstraints=True, preserved_as_paper=False,
            title="Testdocument")

        cb = portal.manage_copyObjects(orig_doc.id)
        portal.manage_pasteObjects(cb)

        new_doc = portal['copy_of_document-1']
        self.assertTrue(new_doc.title == u'copy of Testdocument')

        new_history = pr.getHistory(new_doc)
        # The new history should have an initial version,
        # but existing versions shouldn't be copied
        self.assertEquals(len(new_history), 1)

    def test_default_values(self):
        portal = self.layer['portal']
        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        d1 = createContentInContainer(portal, 'opengever.document.document',
              file=monk_file)
        field = getFields(IDocumentSchema).get('document_date')
        default = queryMultiAdapter(
            (d1, d1.REQUEST, None, field, None, ), IValue, name='default')
        self.assertTrue(default.get(), date.today())

    def test_basedocument(self):
        portal = self.layer['portal']
        d1 = createContentInContainer(
            portal, 'opengever.document.document')

        self.assertTrue(IBaseDocument.providedBy(d1))

    def test_sequence_number(self):
        """All Objects marked as BaseDocuments, should use the same counter."""

        portal = self.layer['portal']
        seqNumb = getUtility(ISequenceNumber)
        d1 = createContentInContainer(portal, 'opengever.document.document')
        b1 = createContentInContainer(portal, 'BaseDocumentFTI')
        d2 = createContentInContainer(portal, 'opengever.document.document')

        self.assertEquals(seqNumb.get_number(d1), 1)
        self.assertEquals(seqNumb.get_number(b1), 2)
        self.assertEquals(seqNumb.get_number(d2), 3)

    def test_reference_number(self):
        """The reference Number Adapter should work
        for all BaseDocument objects."""

        portal = self.layer['portal']
        d1 = createContentInContainer(portal, 'opengever.document.document')
        b1 = createContentInContainer(portal, 'BaseDocumentFTI')
        d2 = createContentInContainer(portal, 'opengever.document.document')

        self.assertEquals(
            getAdapter(d1, IReferenceNumber).get_number(), 'OG / 1')
        self.assertEquals(
            getAdapter(b1, IReferenceNumber).get_number(), 'OG / 2')
        self.assertEquals(
            getAdapter(d2, IReferenceNumber).get_number(), 'OG / 3')

    def test_accessors(self):
        """Test title and descprition accessors."""

        portal = self.layer['portal']
        d1 = createContentInContainer(
            portal, 'opengever.document.document',
            title=u'Test title', description=u'Lorem ipsum')
        self.assertEquals(d1.Title(), u'Test title')
        self.assertEquals(d1.Description(), u'Lorem ipsum')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
