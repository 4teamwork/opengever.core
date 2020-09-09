from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column


class AddIsLocalColumnForGroups(SchemaMigration):
    """Add is local column for groups.
    """

    def migrate(self):
        self.op.add_column(
            'groups', Column('is_local', Boolean, default=False, nullable=True)
        )
