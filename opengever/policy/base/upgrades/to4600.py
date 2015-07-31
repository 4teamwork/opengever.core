from ftw.upgrade import UpgradeStep
from opengever import locking
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import get_tables


class InstallOpengeverLocking(UpgradeStep):

    def __call__(self):
        self.create_locking_tables()
        self.setup_install_profile(
            'profile-opengever.locking:default')

    def create_locking_tables(self):
        """When installing the locking suppackage via upgrade-step we need
        to initialize its database tables.

        If it is installed on an new plone-site `opengever.base.hooks` takes
        care of that.
        """
        Base.metadata.create_all(
            create_session().bind,
            tables=get_tables(locking.model.tables),
            checkfirst=True)
