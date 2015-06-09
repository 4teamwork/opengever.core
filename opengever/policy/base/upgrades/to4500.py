from ftw.upgrade import UpgradeStep


class InstallPloneAppRelationfield(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-plone.app.relationfield:default')
