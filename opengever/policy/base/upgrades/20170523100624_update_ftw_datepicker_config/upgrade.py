from ftw.upgrade import UpgradeStep


class UpdateFtwDatepickerConfig(UpgradeStep):
    """Update ftw.datepicker config.
    """

    def __call__(self):
        self.install_upgrade_profile()
