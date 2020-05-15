from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddFilenameColumnToFavorites(SchemaMigration):
    """Add filename column to favorites.
    """

    def migrate(self):
        self.op.add_column(
            'favorites', Column('filename', String(105), nullable=True)
        )
