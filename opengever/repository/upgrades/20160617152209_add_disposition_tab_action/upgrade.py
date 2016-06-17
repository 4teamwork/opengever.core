from ftw.upgrade import UpgradeStep


class AddDispositionTabAction(UpgradeStep):
    """Add disposition tab action.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.actions_add_type_action(
            'opengever.repository.repositoryroot',
            after='dossiers',
            action_id='dispositions',
            **{'title': 'Dispositions',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': ('opengever.disposition: Add disposition', )})
