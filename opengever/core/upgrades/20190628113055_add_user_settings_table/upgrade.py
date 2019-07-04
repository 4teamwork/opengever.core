from opengever.base.model import USER_ID_LENGTH
from opengever.core.upgrade import SchemaMigration
from opengever.ogds.models.user import User
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String


class AddUserSettingsTable(SchemaMigration):
    """Add user_settings table.
    """

    def migrate(self):
        self.op.create_table(
            'user_settings',
            Column('userid', String(USER_ID_LENGTH),
                   ForeignKey(User.userid), primary_key=True),
            Column('notify_own_actions', Boolean, default=False, nullable=False),
            Column('notify_inbox_actions', Boolean, default=True, nullable=False)
            )

        # On some deployments, these columns had been added to the users table,
        # we drop them if necessary.
        # We do not migrate the data from the user table, but start fresh.
        users = self.metadata.tables.get("users")
        if users.columns.get("notify_own_actions", None) is not None:
            self.op.drop_column('users', 'notify_own_actions')
        if users.columns.get("notify_inbox_actions", None) is not None:
            self.op.drop_column('users', 'notify_inbox_actions')
