from ftw.upgrade import UpgradeStep
from opengever.base import model


class InstallActivity(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.activity:default')
        self.setup_install_profile(
            'profile-collective.js.timeago:default')
        self.create_activity_tables()

    def create_activity_tables(self):
        """When installing the activity suppackage via upgrade-step we need
        to initialize its database tables.

        If it is installed on an new plone-site `opengever.base.hooks` takes
        care of that.
        """

        model.Base.metadata.create_all(model.Session().bind, checkfirst=True)
