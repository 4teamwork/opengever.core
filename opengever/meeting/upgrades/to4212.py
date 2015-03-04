from ftw.upgrade import UpgradeStep


class AddCommitteeOverviewTab(UpgradeStep):

    def __call__(self):
        self.actions_add_type_action(
            'opengever.meeting.committee',
            after='add-membership',
            action_id='overview',
            **{'title': 'overview',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': ('View', )})
