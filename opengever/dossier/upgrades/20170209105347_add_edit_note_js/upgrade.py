from ftw.upgrade import UpgradeStep


class AddEditNoteJs(UpgradeStep):
    """Add edit_note.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
