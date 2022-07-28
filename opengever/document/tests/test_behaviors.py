from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import ISequenceNumber
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.services.sources.get import get_field_by_name
from zc.relation.interfaces import ICatalog
from zope import component
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.intid.interfaces import IIntIds


class TestDocumentNameFromTitle(FunctionalTestCase):

    def test_id_generation(self):
        doc1 = create(Builder('document'))
        doc2 = create(Builder('document'))

        self.assertEquals(1, getUtility(ISequenceNumber).get_number(doc1))
        self.assertEquals('document-1', doc1.id)

        self.assertEquals(2, getUtility(ISequenceNumber).get_number(doc2))
        self.assertEquals('document-2', doc2.id)


class TestRelatedDocuments(IntegrationTestCase):

    def test_relations_get_broken_when_to_object_is_deleted(self):
        self.login(self.manager)
        related_docs = IRelatedDocuments(self.subdocument).relatedItems
        self.assertEqual(1, len(related_docs))
        self.assertFalse(related_docs[0].isBroken())
        self.assertEqual(self.document, related_docs[0].to_object)

        api.content.delete(self.document)
        related_docs = IRelatedDocuments(self.subdocument).relatedItems
        self.assertEqual(1, len(related_docs))
        self.assertTrue(related_docs[0].isBroken())
        self.assertIsNone(related_docs[0].to_object)

    def test_related_items_does_not_include_broken_relations(self):
        self.login(self.manager)
        related_docs = self.subdocument.related_items()
        self.assertEqual(self.document, related_docs[0])

        api.content.delete(self.document)
        related_docs = self.subdocument.related_items()
        self.assertEqual(0, len(related_docs))

    def test_broken_relations_do_not_get_serialized(self):
        self.login(self.manager)
        field = get_field_by_name('relatedItems', self.subdocument)
        serializer = queryMultiAdapter(
            (field, self.subdocument, self.request), IFieldSerializer)

        value = serializer()
        self.assertEqual(1, len(value))
        self.assertEqual(self.document.absolute_url(), value[0]['@id'])

        api.content.delete(self.document)
        value = serializer()
        self.assertEqual(0, len(value))

    def test_relations_get_removed_when_from_object_is_deleted(self):
        self.login(self.manager)
        catalog = component.queryUtility(ICatalog)
        intids = component.queryUtility(IIntIds)
        subsubdoc_id = intids.getId(self.subsubdocument)

        relations = list(catalog.findRelations({'from_id': subsubdoc_id}))
        self.assertEqual(2, len(relations))
        self.assertItemsEqual(
            [self.document, self.subdocument],
            [relation.to_object for relation in relations])
        self.assertItemsEqual(
            [self.document, self.subsubdocument],
            self.subdocument.related_items(include_backrefs=True))

        api.content.delete(self.subsubdocument)
        relations = list(catalog.findRelations({'from_id': subsubdoc_id}))
        self.assertEqual(0, len(relations))
        self.assertItemsEqual(
            [self.document],
            self.subdocument.related_items(include_backrefs=True))
