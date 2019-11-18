from ftw.upgrade import UpgradeStep


class RemoveClosePeriodActionFromCommittee(UpgradeStep):
    """Remove close period action from committee.
    """

    def __call__(self):
        self.actions_remove_type_action(
            'opengever.meeting.committee', 'close-period')
