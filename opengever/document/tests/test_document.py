import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedFile

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.document.tests.layer import Layer

from opengever.document.document import IDocumentSchema


class TestDocumentIntegration(PloneTestCase):

    layer = Layer

    def test_adding(self):
        self.folder.invokeFactory( 'opengever.document.document', 'document1')
        d1 = self.folder['document1']
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
        self.folder.invokeFactory('opengever.document.document', 'document1')
        d1 = self.folder['document1']
        field = IDocumentSchema['file']
        monk_file = NamedFile('bla bla', filename=u'test.txt')
        field.set(d1, monk_file)
        self.assertTrue(field.get(d1).data == 'bla bla')

    def test_digital_available(self):
        monk_file = NamedFile('bla bla', filename=u'test.txt')
        d1 = createContentInContainer(self.folder, 'opengever.document.document',
            file=monk_file)
        self.assertTrue(d1.digital_available==True)
        d2 = createContentInContainer(self.folder, 'opengever.document.document')
        self.assertTrue(d2.digital_available==False)
        d3 = createContentInContainer(self.folder, 'opengever.document.document',
                checkConstraints=True, preserved_as_paper=False)
        self.assertTrue(d3==None)

def test_views(self):
        self.folder.invokeFactory('opengever.document.document', 'document1')
        d1 = self.folder['document1']
        d1.keywords=()
        view = d1.restrictedTraverse('@@view')
        self.failUnless(view())
        tabbed_view = d1.restrictedTraverse('@@tabbed_view')
        self.failUnless(tabbed_view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
