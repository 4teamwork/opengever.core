from ftw.upgrade import UpgradeStep


class EnableTaskTemplatesForMeetingDossiers(UpgradeStep):
    """Enable task-templates for meeting-dossiers.
    """

    def __call__(self):
        self.install_upgrade_profile()
