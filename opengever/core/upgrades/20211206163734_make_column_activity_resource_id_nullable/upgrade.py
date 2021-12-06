from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Integer


class MakeColumnActivityResourceIDNullable(SchemaMigration):
    """Make column Activity.resource_id nullable.
    """

    def migrate(self):
        self.op.alter_column('activities', 'resource_id',
                             existing_type=Integer, nullable=True)
