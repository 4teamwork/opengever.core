from ftw.upgrade import UpgradeStep


class AddTreeview(UpgradeStep):
    """ Enable new treeview profile in opengever.core. """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.treeview:default')
