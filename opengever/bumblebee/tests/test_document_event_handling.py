from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.document.docprops import DocPropertyWriter
from opengever.testing import IntegrationTestCase


class TestDocPropertywriterBumblebeeChecksum(IntegrationTestCase):
    """Test that bumblebee checksum remains up to date after we have modified
    a document with the doc property writer.

    """
    features = ('doc-properties',)

    def test_bumblebee_checksum_updated_when_document_modified(self):
        self.login(self.dossier_responsible)

        pre_update_checksum = IBumblebeeDocument(self.document).get_checksum()

        DocPropertyWriter(self.document).update_doc_properties(only_existing=False)

        post_update_checksum = IBumblebeeDocument(self.document).get_checksum()
        self.assertEqual(
            post_update_checksum,
            IBumblebeeDocument(self.document).update_checksum(),
            "Cached checksum and freshly calculated checksums must match.")
        self.assertNotEqual(
            pre_update_checksum, post_update_checksum,
            "Expected bumblebee checksum to change when the document has been "
            "modified")
