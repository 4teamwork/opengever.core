from ftw.upgrade import UpgradeStep


class HideFtwMailMailInViewlet(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.mail.upgrades:2104')
