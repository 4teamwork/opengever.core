from ftw.upgrade import UpgradeStep


class RemoveCustomCommitteeWorkflowActions(UpgradeStep):
    """Remove custom committee workflow actions.
    """

    workflow_actions_to_remove = [
        'deactivate-committee',
        'reactivate-committee',
    ]

    def __call__(self):
        for action_id in self.workflow_actions_to_remove:
            self.actions_remove_type_action(
                'opengever.meeting.committee', action_id)
