from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddOgdsUserParticipation(SchemaMigration):
    """Add ogds-user participation."""

    def migrate(self):
        self.op.add_column('participations',
                           Column('ogds_userid', String(255)))
