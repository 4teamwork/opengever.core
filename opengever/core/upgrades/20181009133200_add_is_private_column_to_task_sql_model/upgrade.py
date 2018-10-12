from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Boolean


class AddIsPrivateColumnToTaskSQLModel(SchemaMigration):
    """Add is private column to task sql model.
    """

    def migrate(self):
        self.op.add_column(
            'tasks',
            Column('is_private', Boolean))
