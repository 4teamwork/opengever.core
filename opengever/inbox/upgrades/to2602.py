from ftw.upgrade import UpgradeStep


class UpdateForwardingWorkflow(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.inbox:default', steps=['workflow'])
