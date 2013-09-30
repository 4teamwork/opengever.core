from ftw.upgrade import UpgradeStep


class AdjustTabbedviewTabs(UpgradeStep):

    def __call__(self):
        self.remove_inbox_tabs()
        self.add_new_inbox_tabs()

        self.setup_install_profile(
            'profile-opengever.inbox.upgrades:2601')
        self.adjust_yearfolder_action()

    def remove_inbox_tabs(self):
        """Remove actions of no longer used tabs"""

        to_remove = ['assigned_forwardings', 'given_tasks', 'assigned_tasks',
                     'assigned_inbox_tasks', 'issued_inbox_tasks']

        for action_id in to_remove:
            self.actions_remove_type_action('opengever.inbox.inbox', action_id)

    def add_new_inbox_tabs(self):
        """Adds new tabs action for the inbox FTI"""

        self.actions_add_type_action(
            'opengever.inbox.inbox',
            'documents',
            'assigned_inbox_tasks',
            **{'title': 'Inbox Tasks',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': ('View', )})

        self.actions_add_type_action(
            'opengever.inbox.inbox',
            'assigned_inbox_tasks',
            'issued_inbox_tasks',
            **{'title': 'Issued Tasks',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': ('View', )})

    def adjust_yearfolder_action(self):
        """Replace forwardings tab action"""

        self.actions_remove_type_action(
            'opengever.inbox.yearfolder',
            'given_tasks')

        self.actions_add_type_action(
            'opengever.inbox.yearfolder',
            'edit',
            'closed-forwardings',
            **{'title': 'Forwardings',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': ('View', )})
