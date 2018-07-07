from ftw.upgrade import UpgradeStep


class AddMeetingTemplateJ_ssForOrderingTheParargraphs(UpgradeStep):
    """Add meeting template javascript for ordering the paragraphs.
    """

    def __call__(self):
        self.install_upgrade_profile()
