from ftw.upgrade import UpgradeStep


class RenameAddMemberAction(UpgradeStep):

    def __call__(self):
        """Because type actions can be easely updated, we remove and
        re-add the action."""

        self.actions_remove_type_action(
            'opengever.meeting.committeecontainer', 'add-member')

        self.actions_add_type_action(
            'opengever.meeting.committeecontainer',
            after='edit',
            action_id='add-member',
            **{'title': 'Committee Member',
               'action': 'string:${object_url}/add-member',
               'category': 'folder_factories',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': ('opengever.meeting: Add Member', )})
