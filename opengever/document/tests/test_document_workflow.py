from ftw.builder import Builder
from ftw.builder import create
from opengever.document.document import Document
from opengever.testing import IntegrationTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from zExceptions import Unauthorized


class TestDocumentWorkflow(IntegrationTestCase):

    def test_document_draft_state_is_initial_state(self):
        doc = create(Builder('document'))

        self.assertEquals(Document.active_state, api.content.get_state(obj=doc))

    def test_only_manager_can_remove_document(self):
        # Only manager has 'Delete GEVER content' permission by default
        self.login(self.administrator)
        self.trash_documents(self.document)

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.document, transition='document-transition-remove')

        self.login(self.manager)
        api.content.transition(obj=self.document,
                               transition='document-transition-remove')
        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=self.document))

    def test_document_cant_be_removed_if_it_is_not_trashed(self):
        self.login(self.manager)
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.document,
                                   transition='document-transition-remove')

    def test_only_manager_can_restore_document(self):
        self.login(self.manager)
        self.trash_documents(self.document)
        api.content.transition(obj=self.document,
                               transition='document-transition-remove')
        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=self.document))

        with self.login(self.administrator), self.assertRaises(Unauthorized):
            api.content.transition(obj=self.document,
                                   transition='document-transition-restore')

        api.content.transition(obj=self.document,
                               transition='document-transition-restore')

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.document))

    def test_deleting_document_is_only_allowed_for_managers(self):
        self.login(self.administrator)

        with self.assertRaises(Unauthorized):
            api.content.delete(obj=self.document)

        self.login(self.manager)
        api.content.delete(obj=self.document)
