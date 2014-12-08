from ftw.upgrade import UpgradeStep
from opengever.core import model


class InstallMeeting(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.meeting:default')
        self.setup_install_profile(
            'profile-opengever.policy.base.upgrades:4000')
        self.create_meeting_tables()

    def create_meeting_tables(self):
        """When installing meeting via upgrade-step we need to initialize
        its database tables.

        If if is instlalled on an new plone-site `opengever.base.hooks` takes
        care of that.

        """
        model.Base.metadata.create_all(model.Session().bind, checkfirst=True)
