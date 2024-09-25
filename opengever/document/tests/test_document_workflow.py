from base64 import b64encode
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.security import as_internal_workflow_transition
from opengever.document.document import Document
from opengever.document.versioner import Versioner
from opengever.sign.sign import Signer
from opengever.sign.tests.test_sign import DEFAULT_MOCK_RESPONSE
from opengever.sign.tests.test_sign import FROZEN_NOW
from opengever.testing import IntegrationTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from zExceptions import Unauthorized
import re
import requests_mock


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

    def test_document_cannot_be_finalized_if_is_referenced_by_pending_approval_task(self):
        self.login(self.administrator)
        self.task_in_protected_dossier.task_type = 'approval'

        with self.assertRaises(InvalidParameterError):
            api.content.transition(
                obj=self.protected_document_with_task,
                transition=Document.finalize_transition)

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.document))

    def test_limited_admin_can_reopen_finalized_document(self):
        with self.login(self.manager):
            api.content.transition(obj=self.subdocument,
                                   transition=Document.finalize_transition)

        with self.login(self.regular_user), self.assertRaises(InvalidParameterError):
            api.content.transition(
                obj=self.subdocument, transition=Document.reopen_transition)

        self.login(self.limited_admin)
        api.content.transition(obj=self.subdocument,
                               transition=Document.reopen_transition)
        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.subdocument))

    def test_cannot_reopen_finalized_document_referenced_by_pending_approval_task(self):
        self.login(self.manager)
        api.content.transition(obj=self.protected_document_with_task,
                               transition=Document.finalize_transition)

        self.assertFalse(self.task_in_protected_dossier.is_approval_task())
        self.assertIn(
            'document-transition-reopen',
            self.get_workflow_transitions_for(self.protected_document_with_task))

        self.task_in_protected_dossier.task_type = 'approval'
        self.assertTrue(self.task_in_protected_dossier.is_approval_task())
        self.assertNotIn(
            'document-transition-reopen',
            self.get_workflow_transitions_for(self.protected_document_with_task))

        with self.assertRaises(InvalidParameterError):
            api.content.transition(
                obj=self.protected_document_with_task,
                transition=Document.reopen_transition)

        self.set_workflow_state('task-state-tested-and-closed',
                                self.task_in_protected_dossier)

        self.assertIn(
            'document-transition-reopen',
            self.get_workflow_transitions_for(self.protected_document_with_task))
        api.content.transition(
            obj=self.protected_document_with_task,
            transition=Document.reopen_transition)
        self.assertEquals(
            Document.active_state,
            api.content.get_state(obj=self.protected_document_with_task))

    def test_finalizer_can_reopen_document(self):
        self.login(self.regular_user)
        api.content.transition(obj=self.subdocument,
                               transition=Document.finalize_transition)

        # finalizer gets stored on the document
        self.assertEqual(self.subdocument.finalizer, self.regular_user.getId())
        self.assertEquals(Document.final_state,
                          api.content.get_state(obj=self.subdocument))

        api.content.transition(
            obj=self.subdocument, transition=Document.reopen_transition)

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.subdocument))

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

    def test_cannot_start_signing_document_in_draft_state_with_inactive_feature(self):
        self.deactivate_feature('sign')
        self.login(self.manager)

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.document,
                                   transition=Document.draft_signing_transition)

    def test_cannot_start_signing_document_in_final_state_with_inactive_feature(self):
        self.deactivate_feature('sign')
        self.login(self.manager)

        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.document,
                                   transition=Document.final_signing_transition)

    @requests_mock.Mocker()
    def test_can_start_signing_a_document_in_draft_state(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            api.content.transition(obj=self.document,
                                   transition=Document.draft_signing_transition)

        self.assertEquals(Document.signing_state,
                          api.content.get_state(obj=self.document))

        self.assertEqual(self.regular_user.getId(), self.document.finalizer)

        self.assertDictEqual(
            {
                'created': u'2024-02-18T15:45:00',
                'job_id': '1',
                'redirect_url': 'http://external.example.org/signing-requests/123',
                'signers': [
                    {
                        'email': 'foo@example.com',
                        'userid': 'regular_user',
                    }
                ],
                'userid': 'regular_user',
                'version': 0
            }, Signer(self.document).serialize_pending_signing_job())

    @requests_mock.Mocker()
    def test_can_start_signing_a_document_in_final_state(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)

        self.login(self.regular_user)

        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)

        with freeze(FROZEN_NOW):
            api.content.transition(obj=self.document,
                                   transition=Document.final_signing_transition)

        self.assertEquals(Document.signing_state,
                          api.content.get_state(obj=self.document))

        self.assertDictEqual(
            {
                'created': u'2024-02-18T15:45:00',
                'job_id': '1',
                'redirect_url': 'http://external.example.org/signing-requests/123',
                'signers': [
                    {
                        'email': 'foo@example.com',
                        'userid': 'regular_user',
                    }
                ],
                'userid': 'regular_user',
                'version': 0
            }, Signer(self.document).serialize_pending_signing_job())

    @requests_mock.Mocker()
    def test_sign_transition_is_only_for_internal_use(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.regular_user)

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.document,
                                   transition=Document.signing_signed_transition,
                                   transition_params={'filedata': b64encode('<DATA>')})

        self.assertEquals(Document.signing_state,
                          api.content.get_state(obj=self.document))

        with as_internal_workflow_transition():
            api.content.transition(obj=self.document,
                                   transition=Document.signing_signed_transition,
                                   transition_params={'filedata': b64encode('<DATA>')})

        self.assertEquals(Document.signed_state,
                          api.content.get_state(obj=self.document))

    @requests_mock.Mocker()
    def test_sign_transition_creates_a_new_version_with_the_given_data(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.regular_user)

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        self.assertEqual(0, self.document.get_current_version_id(missing_as_zero=True))

        with as_internal_workflow_transition():
            api.content.transition(obj=self.document,
                                   transition=Document.signing_signed_transition,
                                   transition_params={'filedata': b64encode('<DATA>')})

        self.assertEqual(1, self.document.get_current_version_id(missing_as_zero=True))
        signed_version = Versioner(self.document).retrieve(1)
        self.assertEqual(u'<DATA>', signed_version.file.data)

    @requests_mock.Mocker()
    def test_can_abort_signing_document(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        delete_mocker = mocker.delete(re.compile('/signing-jobs/1'))
        self.login(self.regular_user)
        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        self.assertEquals(Document.signing_state,
                          api.content.get_state(obj=self.document))

        api.content.transition(obj=self.document,
                               transition=Document.signing_final_transition)

        self.assertEqual(1, delete_mocker.call_count)
        self.assertEquals(Document.final_state,
                          api.content.get_state(obj=self.document))

    @requests_mock.Mocker()
    def test_can_revise_signed_document(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.regular_user)

        FINALIZED_FILE_DATA = '<FINALIZED_FILE_DATA>'
        SIGNED_FILE_DATA = '<SIGNED_FILE_DATA>'

        self.document.update_file(
            data=FINALIZED_FILE_DATA,
            create_version=True)

        self.assertEqual(1, self.document.get_current_version_id(missing_as_zero=True))

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        with as_internal_workflow_transition():
            api.content.transition(obj=self.document,
                                   transition=Document.signing_signed_transition,
                                   transition_params={'filedata': b64encode(SIGNED_FILE_DATA)})

        self.assertEquals(Document.signed_state,
                          api.content.get_state(obj=self.document))
        self.assertEqual(2, self.document.get_current_version_id(missing_as_zero=True))
        self.assertEqual(SIGNED_FILE_DATA, self.document.file.data)

        api.content.transition(obj=self.document,
                               transition=Document.signed_draft_transition)

        self.assertEquals(Document.active_state,
                          api.content.get_state(obj=self.document))
        self.assertEqual(3, self.document.get_current_version_id(missing_as_zero=True))
        self.assertEqual(FINALIZED_FILE_DATA, self.document.file.data)

    @browsing
    @requests_mock.Mocker()
    def test_signing_document_cannot_be_edited(self, browser, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.administrator, browser)
        browser.open(self.document, view='edit')

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(self.document, view='edit')

    @requests_mock.Mocker()
    def test_signing_document_cannot_be_checked_out(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.administrator)
        self.assertTrue(self.document.is_checkout_permitted())

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        self.assertFalse(self.document.is_checkout_permitted())

    @browsing
    @requests_mock.Mocker()
    def test_signed_document_cannot_be_edited(self, browser, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.administrator, browser)
        browser.open(self.document, view='edit')

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        with as_internal_workflow_transition():
            api.content.transition(obj=self.document,
                                   transition=Document.signing_signed_transition,
                                   transition_params={'filedata': b64encode('<DATA>')})

        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(self.document, view='edit')

    @requests_mock.Mocker()
    def test_signed_document_cannot_be_checked_out(self, mocker):
        self.activate_feature('sign')
        mocker.post(re.compile('/signing-jobs'), json=DEFAULT_MOCK_RESPONSE)
        self.login(self.administrator)
        self.assertTrue(self.document.is_checkout_permitted())

        api.content.transition(obj=self.document,
                               transition=Document.draft_signing_transition)

        with as_internal_workflow_transition():
            api.content.transition(obj=self.document,
                                   transition=Document.signing_signed_transition,
                                   transition_params={'filedata': b64encode('<DATA>')})

        self.assertFalse(self.document.is_checkout_permitted())
