from ftw.upgrade import UpgradeStep
from opengever import contact
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import get_tables


class AddSQLModelForNewContactImplementation(UpgradeStep):
    """Add SQL Model for new contact implementation.
    """

    def __call__(self):
        self.create_contact_tables()

    def create_contact_tables(self):
        """If it is installed on an new plone-site `opengever.base.hooks` takes
        care of that.
        """
        Base.metadata.create_all(
            create_session().bind,
            tables=get_tables(contact.models.tables),
            checkfirst=True)
