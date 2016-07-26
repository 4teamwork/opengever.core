from ftw.upgrade import UpgradeStep


class RemoveTabbedviewActionsOnContacfolderFTI(UpgradeStep):
    """Remove tabbedview actions on contacfolder fti.
    """

    def __call__(self):
        self.actions_remove_type_action(
            'opengever.contact.contactfolder', 'local')
        self.actions_remove_type_action(
            'opengever.contact.contactfolder', 'users')
