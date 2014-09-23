from ftw.upgrade import UpgradeStep


class AddCheckinWithoutCommentAction(UpgradeStep):
    """Adds public_trial index and metadata"""

    def __call__(self):
        self.actions_remove_type_action(
            'opengever.document.document', 'checkin_document')
        self.setup_install_profile(
            'profile-opengever.document.upgrades:4000')
