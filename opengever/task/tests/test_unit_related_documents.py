# coding=UTF-8
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.task.browser.related_documents import \
    RelatedDocumentsCatalogTableSource
from opengever.core.testing import ANNOTATION_LAYER
from plone.uuid.interfaces import IUUID
from zope.interface import Interface
from ftw.table.catalog_source import default_custom_sort


class ExtendQueryWithOrdering(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(ExtendQueryWithOrdering, self).setUp()

        self.brain_1 = self.mocker.proxy(self.create_dummy(), count=False)
        self.expect(self.brain_1.Title).result('Z3')
        self.expect(self.brain_1.document_author).result('author_1')
        self.expect(self.brain_1.indexed_attr).result('indexed_attr_1')
        self.expect(self.brain_1.indexed_attr_new).result('indexed_attr_Z')

        self.brain_2 = self.mocker.proxy(self.create_dummy(), count=False)
        self.expect(self.brain_2.Title).result('Z1')
        self.expect(self.brain_2.document_author).result('author_2')
        self.expect(self.brain_2.indexed_attr).result('indexed_attr_2')
        self.expect(self.brain_2.indexed_attr_new).result('indexed_attr_Y')

        self.brain_3 = self.mocker.proxy(self.create_dummy(), count=False)
        self.expect(self.brain_3.Title).result('Z2')
        self.expect(self.brain_3.document_author).result(None)
        self.expect(self.brain_3.indexed_attr).result('indexed_attr_3')
        self.expect(self.brain_3.indexed_attr_new).result('indexed_attr_X')

        self.sortable_title = self.mocker.replace(
        'opengever.task.browser.related_documents.sortable_title_transform')
        self.expect(self.sortable_title(ANY, ANY)).call(
            lambda x, y: x.Title).count(0, None)

        self.columns = (
            ('', 'Tuple'),
            {},
            {
                'column': 'document_author',
            },
            {
                'column': 'indexed_attr',
                'sort_index': 'sort_index_attr',
                'transform': lambda x, y: x.indexed_attr_new,
            },
        )

        self.request = {}
        self.config = self.mocker.patch(
            self.create_dummy(_custom_sort_method=None))

    def test_no_columns_bad_sort_index(self):

        self.request['sort'] = 'bad_index'

        self.expect(self.config.sort_reverse).result(False).count(0, None)
        self.expect(self.config.columns).result({})

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        self.assertRaises(
            AttributeError,
            source.extend_query_with_ordering,
            [self.brain_1, self.brain_3, self.brain_2])

    def test_no_sort_index(self):

        self.expect(self.config.sort_reverse).result(False).count(0, None)
        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            ['brain1', 'brain3', 'brain2'])

        self.assertEquals(result, ['brain1', 'brain3', 'brain2'])

    def test_not_handled_sort_index(self):

        self.request['sort'] = 'sequence_number'
        self.expect(self.config.sort_reverse).result(False).count(0, None)

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            ['brain1', 'brain3', 'brain2'])

        self.assertEquals(result, ['brain1', 'brain3', 'brain2'])

    def test_custom_sort_indexes(self):

        request1 = {}
        request2 = {}
        request3 = {}

        request1['sort'] = 'document_date'
        request2['sort'] = 'receipt_date'
        request3['sort'] = 'delivery_date'

        self.expect(self.config.sort_reverse).result(False).count(0, None)

        self.replay()

        source1 = RelatedDocumentsCatalogTableSource(
            self.config, request1)
        source2 = RelatedDocumentsCatalogTableSource(
            self.config, request2)
        source3 = RelatedDocumentsCatalogTableSource(
            self.config, request3)

        result1 = source1.extend_query_with_ordering(
            ['brain1', 'brain3', 'brain2'])
        result2 = source2.extend_query_with_ordering(
            ['brain1', 'brain3', 'brain2'])
        result3 = source3.extend_query_with_ordering(
            ['brain1', 'brain3', 'brain2'])

        self.assertEquals(result1, ['brain1', 'brain3', 'brain2'])
        self.assertEquals(result2, ['brain1', 'brain3', 'brain2'])
        self.assertEquals(result3, ['brain1', 'brain3', 'brain2'])

        self.assertEquals(
            source1.config._custom_sort_method, default_custom_sort)
        self.assertEquals(
            source2.config._custom_sort_method, default_custom_sort)
        self.assertEquals(
            source3.config._custom_sort_method, default_custom_sort)

    def test_with_transform_sortable_title(self):

        self.request['sort'] = 'sortable_title'

        self.expect(self.config.sort_reverse).result(False).count(0, None)
        self.expect(self.config.columns).result(self.columns)

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            [self.brain_1, self.brain_3, self.brain_2])

        self.assertEquals(result, [self.brain_2, self.brain_3, self.brain_1])

    def test_with_transform_reverse(self):

        self.request['sort'] = 'sort_index_attr'

        self.expect(self.config.sort_reverse).result(True).count(0, None)
        self.expect(self.config.columns).result(self.columns)

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            [self.brain_1, self.brain_3, self.brain_2])

        self.assertEquals(result, [self.brain_1, self.brain_2, self.brain_3])

    def test_with_transform(self):

        self.request['sort'] = 'sort_index_attr'

        self.expect(self.config.sort_reverse).result(False).count(0, None)
        self.expect(self.config.columns).result(self.columns)

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            [self.brain_1, self.brain_3, self.brain_2])

        self.assertEquals(result, [self.brain_3, self.brain_2, self.brain_1])

    def test_no_transform_reverse(self):

        self.request['sort'] = 'document_author'

        self.expect(self.config.sort_reverse).result(True).count(0, None)
        self.expect(self.config.columns).result(self.columns)

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            [self.brain_1, self.brain_3, self.brain_2])

        self.assertEquals(result, [self.brain_2, self.brain_1, self.brain_3])

    def test_no_transform(self):

        self.request['sort'] = 'document_author'

        self.expect(self.config.sort_reverse).result(False).count(0, None)
        self.expect(self.config.columns).result(self.columns)

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_ordering(
            [self.brain_1, self.brain_3, self.brain_2])

        self.assertEquals(result, [self.brain_3, self.brain_1, self.brain_2])


class ExtendQueryWithTextfilterTests(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(ExtendQueryWithTextfilterTests, self).setUp()

        self.brain_1 = self.mocker.mock(count=False)
        self.expect(self.brain_1.Title).result('Bräin 1')
        self.expect(self.brain_1.document_author).result('author_1')

        self.brain_2 = self.mocker.mock(count=False)
        self.expect(self.brain_2.Title).result('Brain 2')
        self.expect(self.brain_2.document_author).result('author_2')

        self.brain_3 = self.mocker.mock(count=False)
        self.expect(self.brain_3.Title).result('Bräin 3')
        self.expect(self.brain_3.document_author).result(None)

        self.request = {}
        self.config = self.mocker.mock(count=False)

    def test_no_filter(self):

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_textfilter([self.brain_1], '')

        self.assertEquals(result, [self.brain_1])

    def test_no_brains(self):

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_textfilter([], 'filter')

        self.assertEquals(result, [])

    def test_no_matches(self):

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_textfilter(
            [self.brain_1, self.brain_2, self.brain_3], 'no_matches')

        self.assertEquals(result, [])

    def test_with_matches_on_title(self):

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_textfilter(
            [self.brain_1, self.brain_2, self.brain_3], 'Bräin 1')

        self.assertEquals(result, [self.brain_1])

    def test_with_matches_on_author(self):

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.extend_query_with_textfilter(
            [self.brain_1, self.brain_2, self.brain_3], 'author_2')

        self.assertEquals(result, [self.brain_2])


class GetRelatedDocumentsTests(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(GetRelatedDocumentsTests, self).setUp()

        self.doc_rel_1 = self.create_dummy()
        self.doc_rel_1 = self.mocker.proxy(
            self.doc_rel_1, spec=False, count=False)
        self.expect(self.doc_rel_1.to_object).result(self.doc_rel_1)
        self.expect(
            self.doc_rel_1.portal_type).result('opengever.document.document')

        self.doc_rel_2 = self.create_dummy()
        self.doc_rel_2 = self.mocker.proxy(
            self.doc_rel_2, spec=False, count=False)
        self.expect(self.doc_rel_2.to_object).result(self.doc_rel_2)
        self.expect(self.doc_rel_2.portal_type).result('ftw.mail.mail')

        self.doc_rel_3 = self.create_dummy()
        self.doc_rel_3 = self.mocker.proxy(
            self.doc_rel_3, spec=False, count=False)
        self.expect(self.doc_rel_3.to_object).result(self.doc_rel_3)
        self.expect(
            self.doc_rel_3.portal_type).result('not.allowed.contenttype')

        self.doc_rel_4 = self.create_dummy()
        self.doc_rel_4 = self.mocker.proxy(
            self.doc_rel_4, spec=False, count=False)
        self.expect(self.doc_rel_4.to_object).result(self.doc_rel_4)
        self.expect(
            self.doc_rel_4.portal_type).result('opengever.documet.document')

        self.uuid = self.mocker.mock(count=False)
        self.mock_adapter(self.uuid, IUUID, (Interface, ))
        self.expect(self.uuid(ANY)).call(lambda x: x)

        self.to_brain = self.mocker.replace(
            'plone.app.uuid.utils.uuidToCatalogBrain')
        self.expect(
            self.to_brain(self.doc_rel_4)).call(lambda x: None).count(0, None)
        self.expect(self.to_brain(ANY)).call(lambda x: x).count(0, None)

        self.request = {}
        self.config = self.mocker.mock(count=False)

    def test_no_items(self):

        self.expect(self.config.context.relatedItems).result([])

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.get_related_documents()

        self.assertEquals(result, [])

    def test_any_items(self):

        self.expect(self.config.context.relatedItems).result(
            [self.doc_rel_1, self.doc_rel_2])

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.get_related_documents()

        self.assertEquals(result[0].brain, self.doc_rel_1)
        self.assertEquals(result[1].brain, self.doc_rel_2)

    def test_trashed_items(self):

        self.expect(self.config.context.relatedItems).result(
            [self.doc_rel_1, self.doc_rel_4])

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.get_related_documents()

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].brain, self.doc_rel_1)

    def test_bad_item(self):

        self.expect(self.config.context.relatedItems).result(
            [self.doc_rel_3])

        self.replay()

        source = RelatedDocumentsCatalogTableSource(self.config, self.request)

        result = source.get_related_documents()

        self.assertEquals(result, [])


class BuildQueryTests(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(BuildQueryTests, self).setUp()

        self.request = {}
        self.config = self.mocker.mock(count=False)
        self.expect(self.config.filter_text).result('')
        self.expect(self.config.update_config()).result(True)
        self.expect(self.config.get_base_query()).result({})

        self.source = self.mocker.patch(
            RelatedDocumentsCatalogTableSource(self.config, self.request))
        self.expect(self.source.extend_query_with_ordering(ANY)).call(
            lambda x: x)
        self.expect(self.source.extend_query_with_textfilter(ANY, ANY)).call(
            lambda x, y: x)

    def test_ano_documents(self):

        self.expect(self.source.get_containing_documents(ANY)).result([])
        self.expect(self.source.get_related_documents()).result([])

        self.replay()

        result = self.source.build_query()

        self.assertEquals(result, [])

    def test_no_containing(self):

        self.expect(self.source.get_containing_documents(ANY)).result([])
        self.expect(
            self.source.get_related_documents()).result(['doc1', 'doc2'])

        self.replay()

        result = self.source.build_query()

        self.assertEquals(result, ['doc1', 'doc2'])

    def test_no_related(self):

        self.expect(
            self.source.get_containing_documents(ANY)).result(['doc1', 'doc2'])
        self.expect(self.source.get_related_documents()).result([])

        self.replay()

        result = self.source.build_query()

        self.assertEquals(result, ['doc1', 'doc2'])

    def test_with_documents(self):

        self.expect(
            self.source.get_containing_documents(ANY)).result(['doc1', 'doc2'])
        self.expect(
            self.source.get_related_documents()).result(['doc3', 'doc4'])

        self.replay()

        result = self.source.build_query()

        self.assertEquals(result, ['doc1', 'doc2', 'doc3', 'doc4'])
