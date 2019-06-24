from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddNotifyInboxActionsColumnToUserModel(SchemaMigration):
    """Add notify inbox actions column to user model.
    """

    def migrate(self):
        tablename = 'users'
        self.add_column(tablename)
        self.insert_default_value(tablename)
        self.make_column_non_nullable(tablename)

    def add_column(self, tablename):
        self.op.add_column(
            tablename,
            Column('notify_inbox_actions', Boolean, default=True, nullable=True))

    def insert_default_value(self, tablename):
        user_table = table(
            tablename,
            column("userid"),
            column("notify_inbox_actions"))

        self.connection.execute(
            user_table.update().values(notify_inbox_actions=True))

    def make_column_non_nullable(self, tablename):
        self.op.alter_column(tablename, 'notify_inbox_actions',
                             existing_type=Boolean, nullable=False)
