from ftw.upgrade import UpgradeStep


class AddGuardsForDispositionTransitions(UpgradeStep):
    """Add guards for disposition transitions.
    """

    def __call__(self):
        self.install_upgrade_profile()
