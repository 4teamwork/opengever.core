from ftw.upgrade import UpgradeStep


class UpdateImmediateViewForTasks(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.task.upgrades:2602')
