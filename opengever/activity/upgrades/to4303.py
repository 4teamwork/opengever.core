from opengever.core.upgrade import SchemaMigration


class DropPsqlServerDefaults(SchemaMigration):
    """Unify definition of autoincrementing SQL columns.

    Add explicit Sequence to enable autoincremet for oracle.

    Make server-side tables/sequences consistent with other model definitions
    that have been created with Sequence. This migration only applies to a
    Postgres DBMS.

    """
    profileid = 'opengever.activity'
    upgradeid = 4303

    def migrate(self):
        self.drop_psql_server_defaults()

    def drop_psql_server_defaults(self):
        if not self.is_postgres:
            return

        # First remove sequence owner table/column. This also asserts that the
        # specified sequence exists - our updated model relies on postregs'
        # auto-naming.
        self._remove_sequence_owner('activities_id_seq')
        self._remove_sequence_owner('notifications_id_seq')
        self._remove_sequence_owner('resources_id_seq')
        self._remove_sequence_owner('notification_defaults_id_seq')
        self._remove_sequence_owner('watchers_id_seq')

        # Drop server-default that executes auto-increment.
        self._remove_server_default('activities')
        self._remove_server_default('notifications')
        self._remove_server_default('resources')
        self._remove_server_default('notification_defaults')
        self._remove_server_default('watchers')

    def _remove_sequence_owner(self, sequence_name):
        self.op.execute(
            'ALTER SEQUENCE {} OWNED BY NONE'.format(sequence_name))

    def _remove_server_default(self, table_name):
        self.op.alter_column(
            table_name=table_name,
            column_name='id',
            server_default=None,
        )
