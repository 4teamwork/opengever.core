from ftw.upgrade import UpgradeStep
from opengever import meeting
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import get_tables


class InstallMeeting(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.meeting:default')
        self.setup_install_profile(
            'profile-opengever.policy.base.upgrades:4200')
        self.create_meeting_tables()

    def create_meeting_tables(self):
        """When installing meeting via upgrade-step we need to initialize
        its database tables.

        If it is installed on an new plone-site `opengever.base.hooks` takes
        care of that.

        """
        Base.metadata.create_all(
            create_session().bind,
            get_tables(meeting.model.tables),
            checkfirst=True)
