from opengever.testing import IntegrationTestCase
from opengever.workflow.bulk_transition_information import WorkflowBulkTransitionInformation


class TestWorkflowBulkTransitionInformation(IntegrationTestCase):
    def test_can_extract_transition_information_for_a_dossier(self):
        self.login(self.regular_user)

        workflow_data = WorkflowBulkTransitionInformation().extract_transitions(self.dossier)

        self.assertItemsEqual(
            [
                {
                    'source_state_id': 'dossier-state-active',
                    'target_state_id': 'dossier-state-resolved',
                    'transition_id': 'dossier-transition-resolve',
                    'workflow_id': 'opengever_dossier_workflow'
                },
                {
                    'source_state_id': 'dossier-state-resolved',
                    'target_state_id': 'dossier-state-active',
                    'transition_id': 'dossier-transition-reactivate',
                    'workflow_id': 'opengever_dossier_workflow'
                }
            ], workflow_data.serialize())

    def test_can_extract_transition_information_for_a_document(self):
        self.login(self.regular_user)

        workflow_data = WorkflowBulkTransitionInformation().extract_transitions(self.document)

        self.assertItemsEqual(
            [
                {
                    'source_state_id': 'document-state-signing',
                    'target_state_id': 'document-state-final',
                    'transition_id': 'document-transition-signing-final',
                    'workflow_id': 'opengever_document_workflow'
                },
                {
                    'source_state_id': 'document-state-final',
                    'target_state_id': 'document-state-draft',
                    'transition_id': 'document-transition-reopen',
                    'workflow_id': 'opengever_document_workflow'
                },
                {
                    'source_state_id': 'document-state-signed',
                    'target_state_id': 'document-state-draft',
                    'transition_id': 'document-transition-signed-draft',
                    'workflow_id': 'opengever_document_workflow'
                },
                {
                    'source_state_id': 'document-state-draft',
                    'target_state_id': 'document-state-final',
                    'transition_id': 'document-transition-finalize',
                    'workflow_id': 'opengever_document_workflow'
                }], workflow_data.serialize())

    def test_extraction_respects_placeful_worklfows(self):
        self.login(self.workspace_member)

        workflow_data = WorkflowBulkTransitionInformation().extract_transitions(self.workspace_document)
        self.assertEqual('opengever_workspace_document', workflow_data.workflow_id)
