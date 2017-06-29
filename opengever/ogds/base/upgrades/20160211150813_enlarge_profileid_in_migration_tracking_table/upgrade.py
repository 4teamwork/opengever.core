from opengever.core.upgrade import SchemaMigration
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


TRACKING_TABLE_NAME = 'opengever_upgrade_version'


class EnlargeProfileidInMigrationTrackingTable(SchemaMigration):
    """Enlarge profileid in migration tracking table.

    The `profileid` column of the migration tracking table used
    to be `Integer`, which is to small to hold the auto-generated
    upgrade step versions.
    Therefore we need to switch to `BigInteger`.
    """

    def migrate(self):
        if self.is_oracle:
            self.migrate_oracle()

        else:
            self.op.alter_column(
                table_name=TRACKING_TABLE_NAME,
                column_name='upgradeid',
                existing_nullable=False,
                type_=BigInteger,
            )

    def migrate_oracle(self):
        """Because oracle can't handle an Number increase of a column which
        contains data, so we have to rename the column, copy the data over and
        then drop the original column.

        See `ORA-01440' for more details.
        """

        self.rename_original_column()
        self.add_new_column()

        self.migrate_data()

        self.make_upgradeid_non_nullable()
        self.drop_tmp_column()

    def rename_original_column(self):
        self.op.alter_column(
            table_name=TRACKING_TABLE_NAME,
            column_name='upgradeid',
            new_column_name='old_upgradeid',
            existing_nullable=False,
            type_=Integer,
        )

    def add_new_column(self):
        self.op.add_column(
            TRACKING_TABLE_NAME,
            Column('upgradeid', BigInteger, nullable=True)
        )

    def migrate_data(self):
        tracking_table = table(
            TRACKING_TABLE_NAME,
            column("profileid"),
            column("upgradeid"),
            column("old_upgradeid")
        )

        profiles = self.connection.execute(tracking_table.select()).fetchall()

        for profile in profiles:
            self.execute(
                tracking_table.update()
                .values(upgradeid=profile.old_upgradeid)
                .where(tracking_table.columns.profileid == profile.profileid)
            )

    def make_upgradeid_non_nullable(self):
        self.op.alter_column(TRACKING_TABLE_NAME, 'upgradeid',
                             existing_type=BigInteger, nullable=False)

    def drop_tmp_column(self):
        self.op.drop_column(TRACKING_TABLE_NAME, 'old_upgradeid')
