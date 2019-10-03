from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text


class AddUserSettingsColumnSeenTours(SchemaMigration):
    """Add user_settings column seen_tours.
    """

    def migrate(self):
        self.op.add_column(
            'user_settings', Column('_seen_tours', Text, nullable=True))
