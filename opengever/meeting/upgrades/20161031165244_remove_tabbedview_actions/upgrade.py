from ftw.upgrade import UpgradeStep


class RemoveTabbedviewActions(UpgradeStep):
    """Remove tabbedview actions.
    """

    tabbeview_action_ids = [
        'overview',
        'meetings',
        'submittedproposals',
        'memberships'
    ]

    def __call__(self):
        for action_id in self.tabbeview_action_ids:
            self.actions_remove_type_action(
                'opengever.meeting.committee', action_id)
