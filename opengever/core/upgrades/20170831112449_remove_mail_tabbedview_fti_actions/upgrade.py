from ftw.upgrade import UpgradeStep


class RemoveMailTabbedviewFtiActions(UpgradeStep):
    """Remove mail tabbedview fti-actions.
    """

    tabbedview_action_ids = ['overview', 'preview', 'journal', 'sharing']

    def __call__(self):
        self.install_upgrade_profile()

        for action_id in self.tabbedview_action_ids:
            self.actions_remove_type_action('ftw.mail.mail', action_id)
