from ftw.upgrade import UpgradeStep


class AddEditDateOfSubmissionPermission(UpgradeStep):
    """Add EditDateOfSubmission permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
