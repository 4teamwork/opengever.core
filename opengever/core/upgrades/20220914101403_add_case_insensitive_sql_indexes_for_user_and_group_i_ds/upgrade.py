from opengever.core.upgrade import SchemaMigration
from sqlalchemy import text


class AddCaseInsensitiveSQLIndexesForUserAndGroupIDs(SchemaMigration):
    """Add case insensitive SQL indexes for user and group IDs.
    """

    def migrate(self):
        INDEXES = (
            ('ix_users_userid_lower', 'users', [text('lower(userid)')]),
            ('ix_groups_groupid_lower', 'groups', [text('lower(groupid)')]),
        )

        for idx_name, table_name, idx_columns in INDEXES:
            self.create_index_if_not_exists(idx_name, table_name, idx_columns)
