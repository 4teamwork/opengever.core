from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import MockTestCase
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.indexers import DefaultDocumentIndexer
from opengever.document.interfaces import IDocumentIndexer
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
import datetime


class TestDocumentIndexers(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentIndexers, self).setUp()
        self.grant('Manager')

    def test_author_indexers(self):
        """check the author indexers."""

        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One", document_author=u'Hugo Boss',
            document_date=datetime.date(2011,1,1))

        self.assertEquals(obj2brain(doc1).document_author, 'Hugo Boss')
        self.assertEquals(
            index_data_for(doc1).get('sortable_author'),
            u'Hugo Boss')

        # without a author
        doc1.document_author = None
        doc1.reindexObject()

        self.assertEquals(obj2brain(doc1).document_author, None)
        self.assertEquals(
            index_data_for(doc1).get('sortable_author'), u'')

        # with a non-ascii characters including author

        doc1.document_author = u'H\xfcgo B\xf6ss'
        doc1.reindexObject()

        self.assertEquals(
            obj2brain(doc1).document_author, 'H\xc3\xbcgo B\xc3\xb6ss')
        self.assertEquals(
            index_data_for(doc1).get('sortable_author'), u'H\xfcgo B\xf6ss')

    def test_date_indexers(self):
        doc1 = create(Builder('document').having(
            title=u"Doc One",
            document_date=datetime.date(2011,1,1),
            receipt_date=datetime.date(2011, 2, 1)))

        # document_date
        self.assertEquals(
            obj2brain(doc1).document_date, datetime.date(2011, 1, 1))

        # receipt_date
        self.assertEquals(
            obj2brain(doc1).receipt_date, datetime.date(2011, 2, 1))

        # delivery_date
        self.assertEquals(
            obj2brain(doc1).delivery_date, None)

    def test_checked_out_indexer(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_date=datetime.date(2011,1,1),
            receipt_date=datetime.date(2011, 2, 1))

        self.annotations = IAnnotations(doc1)
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = 'TEST_USER_ID'

        doc1.reindexObject()

        self.assertEquals(
            obj2brain(doc1).checked_out, 'TEST_USER_ID')

    def test_searchable_text(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_author=u'Hugo Boss',
            keywords=('foo', 'bar'),
            document_date=datetime.date(2011,1,1),
            receipt_date=datetime.date(2011, 2, 1))

        self.assertEquals(
            index_data_for(doc1).get('SearchableText'),
            ['doc', 'one', 'foo', 'bar', 'hugo', 'boss', 'og', '1', '1'])

    def test_full_text_indexing_with_plain_text(self):
        sample_file = NamedBlobFile('foobar barfoo', filename=u'test.txt')
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_author=u'Hugo Boss',
            file=sample_file)

        searchable_text = index_data_for(doc1).get('SearchableText')
        self.assertIn('foobar', searchable_text)
        self.assertIn('barfoo', searchable_text)

    def test_indexer_picks_correct_doc_indexer_adapter_by_default(self):
        sample_file = NamedBlobFile('foo', filename=u'test.txt')
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_author=u'Hugo Boss',
            file=sample_file)

        fulltext_indexer = getAdapter(doc1, IDocumentIndexer)
        self.assertEquals(fulltext_indexer.__class__,
                          DefaultDocumentIndexer)


class TestDefaultDocumentIndexer(MockTestCase):

    def test_default_document_indexer_calls_portal_transforms_correctly(self):
        # Sample file conforming to NamedFile interface
        filename = 'test.txt'
        mimetype = 'application/pdf'
        data = 'foo'

        sample_blob = self.mocker.mock()
        sample_file = self.mocker.mock()
        self.expect(sample_file._blob).result(sample_blob)
        self.expect(sample_file.data).result(data)
        self.expect(sample_file.filename).result(filename)
        self.expect(sample_file.contentType).result(mimetype)

        # Sample document containing our file
        doc1 = self.mocker.mock()
        self.expect(doc1.file).result(sample_file).count(1, None)

        # datastream returned by transform
        expected_fulltext = 'FULLTEXT'
        stream = self.mocker.mock()
        self.expect(stream.getData()).result(expected_fulltext)

        # Mock the portal_transforms tool
        mock_portal_transforms = self.mocker.mock()
        self.expect(mock_portal_transforms.convertTo(
                'text/plain',
                data,
                mimetype=mimetype,
                filename=filename,
                object=sample_blob)).result(stream)
        self.mock_tool(mock_portal_transforms, "portal_transforms")

        self.replay()

        default_doc_indexer = DefaultDocumentIndexer(doc1)
        fulltext = default_doc_indexer.extract_text()
        self.assertEquals(expected_fulltext, fulltext)

    def test_default_document_catches_transform_exceptions(self):
        # Sample file conforming to NamedFile interface
        filename = 'test.txt'
        mimetype = 'application/pdf'
        data = 'foo'

        sample_blob = self.mocker.mock()
        sample_file = self.mocker.mock()
        self.expect(sample_file._blob).result(sample_blob)
        self.expect(sample_file.data).result(data)
        self.expect(sample_file.filename).result(filename)
        self.expect(sample_file.contentType).result(mimetype)

        # Sample document containing our file
        doc1 = self.mocker.mock()
        self.expect(doc1.file).result(sample_file).count(1, None)

        def raise_transform_exception(*args, **kwargs):
            raise Exception("This transform failed!")

        # Mock the portal_transforms tool to raise an exception
        mock_portal_transforms = self.mocker.mock()
        self.expect(mock_portal_transforms.convertTo(
                'text/plain',
                data,
                mimetype=mimetype,
                filename=filename,
                object=sample_blob)).call(raise_transform_exception)
        self.mock_tool(mock_portal_transforms, "portal_transforms")

        self.replay()

        default_doc_indexer = DefaultDocumentIndexer(doc1)
        try:
            fulltext = default_doc_indexer.extract_text()
        except:
            self.fail("extract_text() didn't catch exception raised "
                      "by transform!")
        self.assertEquals('', fulltext)
