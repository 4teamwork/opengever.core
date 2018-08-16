from ftw.upgrade import UpgradeStep


class CreateProposalUnavailableIfMeetingFeatureDisabled(UpgradeStep):
    """Create proposal unavailable if meeting feature disabled.
    """

    def __call__(self):
        self.install_upgrade_profile()
