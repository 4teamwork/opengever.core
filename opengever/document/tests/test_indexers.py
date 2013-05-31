from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import index_data_for
from plone.dexterity.utils import createContentInContainer
from zope.annotation.interfaces import IAnnotations
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
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_date=datetime.date(2011,1,1),
            receipt_date=datetime.date(2011, 2, 1))

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
