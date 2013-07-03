from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import ISequenceNumber
from opengever.testing import FunctionalTestCase
from zope.component import getUtility


class TestDocumentNameFromTitle(FunctionalTestCase):

    def test_id_generation(self):
        doc1 = create(Builder('document'))
        doc2 = create(Builder('document'))

        self.assertEquals(1, getUtility(ISequenceNumber).get_number(doc1))
        self.assertEquals('document-1', doc1.id)

        self.assertEquals(2, getUtility(ISequenceNumber).get_number(doc2))
        self.assertEquals('document-2', doc2.id)
