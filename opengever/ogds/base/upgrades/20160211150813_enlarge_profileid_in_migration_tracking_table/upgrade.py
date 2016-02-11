from opengever.core.upgrade import SchemaMigration
from sqlalchemy import BigInteger


class EnlargeProfileidInMigrationTrackingTable(SchemaMigration):
    """Enlarge profileid in migration tracking table.

    The `profileid` column of the migration tracking table used
    to be `Integer`, which is to small to hold the auto-generated
    upgrade step versions.
    Therefore we need to switch to `BigInteger`.
    """

    def migrate(self):
        self.op.alter_column(
            table_name='opengever_upgrade_version',
            column_name='upgradeid',
            existing_nullable=False,
            type_=BigInteger,
        )
