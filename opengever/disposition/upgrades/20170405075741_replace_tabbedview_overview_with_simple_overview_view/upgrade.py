from ftw.upgrade import UpgradeStep


class ReplaceTabbedviewOverviewWithSimpleOverviewView(UpgradeStep):
    """Replace tabbedview-overview with simple overview view.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.actions_remove_type_action(
            'opengever.disposition.disposition', 'overview')
