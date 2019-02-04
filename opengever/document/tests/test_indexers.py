from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from ftw.testing import MockTestCase
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.core.testing import COMPONENT_UNIT_TESTING
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.indexers import DefaultDocumentIndexer
from opengever.document.indexers import filename as filename_indexer
from opengever.document.indexers import metadata
from opengever.document.interfaces import IDocumentIndexer
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component.hooks import setSite
import datetime
import pytz


class TestDocumentIndexers(FunctionalTestCase):

    def test_sortable_title_indexer_accomodates_padding_for_five_numbers(self):
        numeric_part = "1 2 3 4 5"
        alphabetic_part = u"".join(["a" for i in range(CONTENT_TITLE_LENGTH
                                                       - len(numeric_part))])
        title = numeric_part + alphabetic_part
        document = create(Builder("document").titled(title))

        self.assertEquals(
            '0001 0002 0003 0004 0005' + alphabetic_part,
            index_data_for(document).get('sortable_title'))

    def test_author_indexers(self):
        """check the author indexers."""

        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One", document_author=u'Hugo Boss',
            document_date=datetime.date(2011, 1, 1))

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

    def test_filesize_indexers(self):
        document = create(
            Builder("document")
            .attach_file_containing(u"content", name=u"file.txt")
        )
        document.reindexObject()
        self.assertEqual(7, index_data_for(document).get('filesize'))
        self.assertEqual(7, obj2brain(document).filesize)

        document.file = None
        document.reindexObject()
        self.assertEqual(0, index_data_for(document).get('filesize'))
        self.assertEqual(0, obj2brain(document).filesize)

    def test_filename_indexers(self):
        document = create(
            Builder("document")
            .titled(u'D\xf6k\xfcm\xe4nt')
            .attach_file_containing(u"content", name=u"file.txt")
        )
        document.reindexObject()
        self.assertEqual(u'Doekuemaent.txt', filename_indexer(document)())
        self.assertEqual(u'Doekuemaent.txt', obj2brain(document).filename)

        document.file = None
        document.reindexObject()
        self.assertEqual(u'', filename_indexer(document)())
        self.assertEqual(u'', obj2brain(document).filename)

    def test_file_extension_indexers(self):
        document = create(
            Builder("document")
            .titled(u'D\xf6k\xfcm\xe4nt')
            .attach_file_containing(u"content", name=u"file.txt")
        )
        document.reindexObject()
        self.assertEqual(u'.txt', index_data_for(document).get('file_extension'))
        self.assertEqual(u'.txt', obj2brain(document).file_extension)

        document.file = None
        document.reindexObject()
        self.assertEqual(u'', index_data_for(document).get('file_extension'))
        self.assertEqual(u'', obj2brain(document).file_extension)

    def test_date_indexers(self):
        creation_date = datetime.datetime(2016, 1, 1, 0, 0, tzinfo=pytz.UTC)
        with freeze(creation_date):
            doc1 = create(Builder('document').having(
                title=u"Doc One",
                document_date=datetime.date(2011, 1, 1),
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

        # changed
        self.assertEquals(
            obj2brain(doc1).changed, creation_date)

    def test_checked_out_indexer(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_date=datetime.date(2011, 1, 1),
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
            document_date=datetime.date(2011, 1, 1),
            receipt_date=datetime.date(2011, 2, 1))

        self.assertItemsEqual(
            ['doc', 'one', 'foo', 'bar', 'hugo', 'boss', 'client1', '1', '1'],
            index_data_for(doc1).get('SearchableText')
            )

    def test_external_reference(self):
        doc = create(Builder('document').having(
            author=u'Hugo Boss',
            title=u'Docment',
            foreign_reference=u'qpr-900-9001-\xf8'))

        self.assertEquals(
            u'qpr-900-9001-\xf8',
            index_data_for(doc).get('external_reference'))

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

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = self.portal.portal_catalog

        create(Builder("document")
               .having(keywords=(u'Keyword 1', u'Keyword with \xf6')))

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')

    def test_metadata_contains_reference_number(self):
        doc = create(Builder("document"))
        self.assertEqual(metadata(doc)(), 'Client1 / 1')

    def test_metadata_contains_description(self):
        doc = create(Builder("document").having(description=u'Foo bar baz.'))
        self.assertEqual(metadata(doc)(), 'Client1 / 1 Foo bar baz.')

    def test_metadata_contains_keywords(self):
        doc = create(Builder("document").having(keywords=(u'Foo', u'Bar')))
        self.assertEqual(metadata(doc)(), 'Client1 / 1 Foo Bar')

    def test_metadata_contains_foreign_reference(self):
        doc = create(Builder("document").having(foreign_reference=u'Ref 123'))
        self.assertEqual(metadata(doc)(), 'Client1 / 1 Ref 123')


class TestDefaultDocumentIndexer(MockTestCase):
    layer = COMPONENT_UNIT_TESTING

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
        self.expect(doc1.get_file()).result(sample_file).count(1, None)

        # datastream returned by transform
        expected_fulltext = 'FULLTEXT'
        stream = self.mocker.mock()
        self.expect(stream.getData()).result(expected_fulltext)

        # Mock portal object for getSite()
        site = self.providing_stub(interfaces=[ISiteRoot])
        self.expect(site.aq_chain).result([site])
        setSite(site)

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
        self.expect(doc1.get_file()).result(sample_file).count(1, None)

        def raise_transform_exception(*args, **kwargs):
            raise Exception("This transform failed!")

        # Mock portal object for getSite()
        site = self.providing_stub(interfaces=[ISiteRoot])
        self.expect(site.aq_chain).result([site])
        setSite(site)

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
        except:  # noqa - this bare except is the whole point of the test
            self.fail("extract_text() didn't catch exception raised "
                      "by transform!")
        self.assertEquals('', fulltext)
