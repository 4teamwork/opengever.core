from plone import api


class WorkflowTransitionsData(object):
    def __init__(self, workflow_id, transitions):
        self.workflow_id = workflow_id
        self.transitions = transitions

    def serialize(self):
        serialized_transition_data = []
        for transition_data in self.transitions:
            serialized_transition_data.append({
                'workflow_id': self.workflow_id,
                'source_state_id': transition_data.get('state').getId(),
                'target_state_id': transition_data.get('transition').new_state_id,
                'transition_id': transition_data.get('transition').getId(),
            })

        return serialized_transition_data


class WorkflowBulkTransitionInformation(object):
    # Only whitelist well tested transitions here
    TRANSITION_WHITELIST = set([
        'dossier-transition-resolve',
        'dossier-transition-reactivate',
        'document-transition-finalize',
        'document-transition-reopen',
        'document-transition-signed-draft',
        'document-transition-signing-final',
    ])

    def __init__(self):
        self.wftool = api.portal.get_tool('portal_workflow')
        self.state_transitions = {}

    def extract_transitions(self, obj):
        """Extracts all transitions related to the given objects workflow.

        Caution: this function does not return transitions possible for this
        object. Instead, it will lookup the assigned workflow of the given
        object and returns all transitions for each state assigned to the
        workklow without any permission check.
        """
        workflow_chain = self.wftool.getWorkflowsFor(obj)
        if not workflow_chain:
            return WorkflowTransitionsData(None, [])

        workflow = workflow_chain[0]
        available_transitions = []

        for state in workflow.states.values():
            transition_ids = filter(
                lambda transition_id: transition_id in self.TRANSITION_WHITELIST,
                state.getTransitions())

            for transition_id in transition_ids:
                transition = workflow.transitions[transition_id]
                available_transitions.append({
                    'state': state,
                    'transition': transition,
                })

        return WorkflowTransitionsData(
            workflow_id=workflow.getId(),
            transitions=available_transitions,
        )
