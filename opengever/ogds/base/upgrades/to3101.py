from ftw.upgrade import UpgradeStep
from opengever.base.model import create_session
from opengever.ogds.models.utils import alter_column_length


class IncreaseUserAndGroupIDColumnLengths(UpgradeStep):
    """Increase UserID and GroupID column lengths in OGDS SQL schema."""

    def __call__(self):
        session = create_session()
        for tbl_name, col_name, new_length in [('users', 'userid', 255),
                                               ('groups', 'groupid', 255),
                                               ]:
            alter_column_length(session, tbl_name, col_name, new_length)
