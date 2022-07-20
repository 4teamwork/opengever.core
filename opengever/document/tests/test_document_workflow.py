from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
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

    def test_document_can_be_finalized_with_edit_permission(self):
        self.login(self.regular_user)
        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)
        self.assertEquals(Document.final_state,
                          api.content.get_state(obj=self.document))

    def test_document_cannot_be_finalized_if_checked_out(self):
        self.login(self.administrator)

        self.checkout_document(self.document)

        with self.assertRaises(InvalidParameterError):
            api.content.transition(
                obj=self.document, transition=Document.finalize_transition)

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.document))

    def test_limited_admin_can_reopen_finalized_document(self):
        with self.login(self.manager):
            api.content.transition(obj=self.document,
                                   transition=Document.finalize_transition)

        with self.login(self.regular_user), self.assertRaises(InvalidParameterError):
            api.content.transition(
                obj=self.document, transition=Document.reopen_transition)

        self.login(self.limited_admin)
        api.content.transition(obj=self.document,
                               transition=Document.reopen_transition)
        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.document))

    def test_finalizer_can_reopen_document(self):
        self.login(self.regular_user)
        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)

        self.assertEquals(Document.final_state,
                          api.content.get_state(obj=self.document))

        api.content.transition(
            obj=self.document, transition=Document.reopen_transition)

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.document))

    def test_finalized_document_cannot_be_checked_out(self):
        self.login(self.administrator)
        self.assertTrue(self.document.is_checkout_permitted())

        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)

        self.assertFalse(self.document.is_checkout_permitted())

    @browsing
    def test_finalized_document_cannot_be_edited(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.document, view='edit')

        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)

        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(self.document, view='edit')
