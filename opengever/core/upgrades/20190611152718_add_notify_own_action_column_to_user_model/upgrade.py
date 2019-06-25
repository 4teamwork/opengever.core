from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddNotifyOwnActionColumnToUserModel(SchemaMigration):
    """Add notify own action column to user model.
    """

    def migrate(self):
        tablename = 'users'
        self.add_column(tablename)
        self.insert_default_value(tablename)
        self.make_column_non_nullable(tablename)

    def add_column(self, tablename):
        self.op.add_column(
            tablename,
            Column('notify_own_actions', Boolean, default=False, nullable=True))

    def insert_default_value(self, tablename):
        user_table = table(
            tablename,
            column("userid"),
            column("notify_own_actions"))

        self.connection.execute(
            user_table.update().values(notify_own_actions=False))

    def make_column_non_nullable(self, tablename):
        self.op.alter_column(tablename, 'notify_own_actions',
                             existing_type=Boolean, nullable=False)
