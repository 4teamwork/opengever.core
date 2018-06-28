from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


UID_LENGTH = 36


class IncreaseUIDColumnLengthInFavoritesModel(SchemaMigration):
    """Increase UID column length in favorites model.
    """

    def migrate(self):
        self.raise_column_length()

    def raise_column_length(self):

        # add new column with the new size
        self.op.add_column(
            'favorites',
            Column('tmp_plone_uid', String(UID_LENGTH)))

        # migrate_data
        _table = table(
            'favorites',
            column("id"),
            column('plone_uid'),
            column('tmp_plone_uid'))

        items = self.connection.execute(_table.select()).fetchall()
        for item in items:
            self.execute(
                _table.update()
                .values(tmp_plone_uid=item.plone_uid)
                .where(_table.columns.id == item.id)
            )

        # drop old column
        self.op.drop_column('favorites', 'plone_uid')

        # rename new column
        self.op.alter_column('favorites',
                             'tmp_plone_uid',
                             new_column_name='plone_uid')
