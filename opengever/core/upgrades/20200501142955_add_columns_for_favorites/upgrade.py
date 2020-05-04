from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String


class AddColumnsForFavorites(SchemaMigration):
    """Add columns for favorites.
    """

    def migrate(self):
        self.op.add_column(
            'favorites', Column('review_state', String(255), nullable=True)
        )
        self.op.add_column(
            'favorites', Column('is_subdossier', Boolean, nullable=True)
        )
        self.op.add_column(
            'favorites', Column('is_leafnode', Boolean, nullable=True)
        )
