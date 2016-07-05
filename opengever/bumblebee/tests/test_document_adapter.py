from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.testing import FunctionalTestCase


class TestDocumentAdapter(FunctionalTestCase):

    def test_document_with_file_is_digitally_available(self):
        document_with_file = create(Builder("document").with_dummy_content())
        self.assertTrue(
            IBumblebeeDocument(document_with_file).is_convertable())

    def test_document_without_file_is_not_digitally_available(self):
        document_without_file = create(Builder("document"))
        self.assertFalse(
            IBumblebeeDocument(document_without_file).is_convertable())
