from zope.component import createObject
from zope.component import queryUtility
from zope.interface import Invalid

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedFile

from opengever.document.testing import OPENGEVER_DOCUMENT_INTEGRATION_TESTING

from opengever.document.document import IDocumentSchema
import unittest2 as unittest

class TestDocumentIntegration(unittest.TestCase):

    layer = OPENGEVER_DOCUMENT_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory( 'opengever.document.document', 'document1')
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
        monk_file = NamedFile('bla bla', filename=u'test.txt')
        field.set(d1, monk_file)
        self.assertTrue(field.get(d1).data == 'bla bla')

    def test_digitally_available(self):
        portal = self.layer['portal']
        monk_file = NamedFile('bla bla', filename=u'test.txt')
        d1 = createContentInContainer(portal, 'opengever.document.document',
            file=monk_file)
        self.assertTrue(d1.digitally_available==True)
        d2 = createContentInContainer(portal, 'opengever.document.document')
        self.assertTrue(d2.digitally_available==False)

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
        d1.keywords=()

        # fake the request
        portal.REQUEST['ACTUAL_URL'] = d1.absolute_url()

        view = d1.restrictedTraverse('@@view')
        self.failUnless(view())
        tabbed_view = d1.restrictedTraverse('@@tabbed_view')
        self.failUnless(tabbed_view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
