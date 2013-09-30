from ftw.upgrade import UpgradeStep


class UpdateTaskReportAction(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.globalindex.upgrades:2601')
