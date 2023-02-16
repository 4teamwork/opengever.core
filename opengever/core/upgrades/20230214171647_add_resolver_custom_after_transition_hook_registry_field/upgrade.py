from ftw.upgrade import UpgradeStep


class AddResolverCustomAfterTransitionHookRegistryField(UpgradeStep):
    """Add resolver_custom_after_transition_hook registry field.
    """

    def __call__(self):
        self.install_upgrade_profile()
