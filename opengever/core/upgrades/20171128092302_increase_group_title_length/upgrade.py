from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


GROUP_TITLE_LENGTH = 255


class IncreaseGroupTitleLength(SchemaMigration):
    """Increase group title length.
    """

    def migrate(self):
        self.op.alter_column(
            'groups',
            'title',
            type_=String(GROUP_TITLE_LENGTH),
            existing_nullable=True,
            existing_type=String(50))
