from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddExternalResourceUrlColumnForActivities(SchemaMigration):
    """Add external_resource_url column for Activities.
    """

    def migrate(self):
        self.op.add_column(
            'activities', Column(
                'external_resource_url', String(255), nullable=True))
