from opengever.core.upgrade import SchemaMigration
from sqlalchemy import text


class AddCaseInsensitiveSQLIndexForGroupsUsersUserid(SchemaMigration):
    """Add case insensitive SQL index for groups_users.userid.
    """

    def migrate(self):
        INDEXES = (
            ('ix_groups_users_userid_lower', 'groups_users', [text('lower(userid)')]),
        )

        for idx_name, table_name, idx_columns in INDEXES:
            self.op.create_index(idx_name, table_name, idx_columns)
