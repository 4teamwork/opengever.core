from opengever.core.upgrade import SchemaMigration


class AddUniqueConstraintForTheFavoritesTable(SchemaMigration):
    """Add unique constraint for the favorites table.
    """

    def migrate(self):
        self.op.create_unique_constraint(
            'ix_favorites_unique',
            'favorites',
            ['admin_unit_id', 'int_id', 'userid'])
