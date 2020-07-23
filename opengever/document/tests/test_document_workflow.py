from ftw.builder import Builder
from ftw.builder import create
from opengever.document.document import Document
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from zExceptions import Unauthorized
import transaction


class TestDocumentWorkflow(FunctionalTestCase):

    def test_document_draft_state_is_initial_state(self):
        doc = create(Builder('document'))

        self.assertEquals(Document.active_state, api.content.get_state(obj=doc))

    def change_user(self):
        create_plone_user(self.portal, 'hugo.boss')
        self.login(user_id='hugo.boss')
        setRoles(self.portal, 'hugo.boss', ['Contributor', 'Editor', 'Reviewer', 'Publisher'])
        transaction.commit()

    def test_document_can_be_removed_with_remove_gever_content_permission(self):
        self.grant('Manager')
        doc = create(Builder('document').trashed())
        api.content.transition(obj=doc,
                               transition='document-transition-remove')
        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=doc))

    def test_document_cant_be_removed_if_it_is_not_trashed(self):
        doc = create(Builder('document'))
        self.grant('Manager')
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=doc, transition='mail-transition-remove')

    def test_document_cant_be_removed_without_remove_gever_content_permission(self):
        # Only manager has 'Delete GEVER content' permission by default
        self.grant('Manager')
        doc = create(Builder('document').trashed())
        self.change_user()
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=doc, transition='document-transition-remove')

    def test_document_can_only_be_restored_with_manage_portal_permission(self):
        doc = create(Builder('document').removed())

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=doc, transition='document-transition-restore')

        self.grant('Manager')
        api.content.transition(obj=doc,
                               transition='document-transition-restore')

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=doc))

    def test_deleting_document_is_only_allowed_for_managers(self):
        doc = create(Builder('document'))

        with self.assertRaises(Unauthorized):
            api.content.delete(obj=doc)
