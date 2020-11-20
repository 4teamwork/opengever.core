from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedDocuments
from opengever.workspaceclient.linked_documents import AlreadyLinkedError
from opengever.workspaceclient.linked_documents import LinkedDocuments
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass


class TestLinkedDocumentsAdapter(IntegrationTestCase):

    def test_implements_interface(self):
        verifyClass(ILinkedDocuments, LinkedDocuments)

    def test_can_link_several_workspace_docs_to_gever_doc(self):
        self.login(self.workspace_member)

        adapter = ILinkedDocuments(self.document)
        adapter.link_workspace_document(IUUID(self.workspace_document))
        adapter.link_workspace_document(IUUID(self.workspace_folder_document))

        expected_links = [
            {'UID': IUUID(self.workspace_document)},
            {'UID': IUUID(self.workspace_folder_document)},
        ]

        self.assertIsInstance(adapter.linked_workspace_documents, list)
        self.assertEqual(expected_links, adapter.linked_workspace_documents)

        self.assertEqual({
            'workspace_documents': expected_links,
            'gever_document': None},
            adapter.serialize())

    def test_can_link_gever_doc_to_workspace_doc(self):
        self.login(self.workspace_member)

        adapter = ILinkedDocuments(self.workspace_document)
        adapter.link_gever_document(IUUID(self.document))

        expected_link = {'UID': IUUID(self.document)}

        self.assertIsInstance(adapter.linked_gever_document, dict)
        self.assertEqual(expected_link, adapter.linked_gever_document)

        self.assertEqual({
            'workspace_documents': [],
            'gever_document': expected_link},
            adapter.serialize())

    def test_cannot_overwrite_existing_link_to_gever_doc(self):
        self.login(self.workspace_member)

        adapter = ILinkedDocuments(self.workspace_document)
        adapter.link_gever_document(IUUID(self.document))

        with self.assertRaises(AlreadyLinkedError):
            adapter.link_gever_document(IUUID(self.subdocument))

    def test_cannot_add_duplicate_links_to_workspace_docs(self):
        self.login(self.workspace_member)

        adapter = ILinkedDocuments(self.document)
        adapter.link_workspace_document(IUUID(self.workspace_document))

        with self.assertRaises(AlreadyLinkedError):
            adapter.link_workspace_document(IUUID(self.workspace_document))

    def test_reading_properties_does_not_result_in_write_to_annotations(self):
        self.login(self.workspace_member)

        adapter = ILinkedDocuments(self.document)

        adapter.linked_workspace_documents
        adapter.linked_gever_document

        annotations = IAnnotations(self.document)
        self.assertNotIn(adapter.storage_key, annotations.keys())
