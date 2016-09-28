from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddDepartmentColumnToOrgrole(SchemaMigration):
    """Add department column to orgrole.
    """

    def migrate(self):
        self.op.add_column('org_roles',
                           Column('department', String(255)))
