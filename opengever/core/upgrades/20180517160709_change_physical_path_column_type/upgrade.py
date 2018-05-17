from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Text
from sqlalchemy import String


class ChangePhysicalPathColumnType(SchemaMigration):
    """Change physical path column type.
    """

    def migrate(self):
        self.op.alter_column(
            'tasks',
            'physical_path',
            type_=Text,
            existing_nullable=True,
            existing_type=String(256))

        self.op.alter_column(
            'proposals',
            'physical_path',
            type_=Text,
            existing_nullable=False,
            existing_type=String(256))

        self.op.alter_column(
            'proposals',
            'submitted_physical_path',
            type_=Text,
            existing_nullable=True,
            existing_type=String(256))

        self.op.alter_column(
            'committees',
            'physical_path',
            type_=Text,
            existing_nullable=False,
            existing_type=String(256))
