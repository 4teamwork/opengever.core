from ftw.upgrade import UpgradeStep


class DisableQuickuploadOverride(UpgradeStep):
    """Disable quickupload override and unique id.

    The override default in collective.quickupload was inconsistent in the
    default profile and in the upgrade step.

    Even though this setting does not affect us currently this upgrade-step
    makes sure that all of our installations have the same setting. You never
    know ...

    Also see https://github.com/collective/collective.quickupload/pull/60.

    """
    def __call__(self):
        self.install_upgrade_profile()
