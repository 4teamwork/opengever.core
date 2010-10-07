import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedFile

from Products.PloneTestCase.ptc import PloneTestCase
from opengever.document.tests.layer import Layer

from opengever.document.document import IDocumentSchema
from opengever.document.staging.manager import ICheckinCheckoutManager


class TestDocumentIntegration(PloneTestCase):

    layer = Layer

    def test_adding(self):
        self.folder.invokeFactory('opengever.document.document', 'document1')
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
        monk_file = NamedFile('bla bla', filename='test.txt')
        field.set(d1, monk_file)
        self.assertTrue(field.get(d1).data == 'bla bla')

    def test_checkout_checkin(self):
        self.folder.invokeFactory('opengever.document.document', 'document1')
        doc1 = self.folder['document1']

        pw = self.folder.portal_workflow
        pa = self.folder.portal_archivist
        history = pa.getHistoryMetadata(doc1)

        self.assertEquals(
                history.getLength(doc1),
                1)

        manager1 = ICheckinCheckoutManager(doc1)
        copy_of_doc1 = manager1.checkout('first checkout')

        self.assertEquals(
                pw.getInfoFor(doc1, 'review_state'),
                'checked_out')
        self.assertEquals(
                pw.getInfoFor(copy_of_doc1, 'review_state'),
                'working_copy')
        self.assertEquals(
                history.getLength(doc1),
                1)

        manager2 = ICheckinCheckoutManager(copy_of_doc1)
        doc1_ = manager2.checkin('first checkin')

        self.assertEquals(
                doc1,
                doc1_)
        self.assertEquals(
                history.getLength(doc1),
                2)

        copy2_of_doc1 = manager1.checkout('second checkout')
        manager3 = ICheckinCheckoutManager(copy2_of_doc1)
        manager3.checkin('second checkin')

        self.assertEquals(
                history.getLength(doc1),
                3)


    # def test_view(self):
    #     self.folder.invokeFactory('opengever.document.document', 'document1')
    #     d1 = self.folder['document1']
    #     d1.keywords=()
    #     view = d1.restrictedTraverse('@@view')
    #     self.failUnless(view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
