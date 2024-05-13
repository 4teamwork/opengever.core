from opengever.core.upgrade import SchemaMigration


class RemoveObjectSidColumn(SchemaMigration):
    """Remove ObjectSid column.
    """

    def migrate(self):
        self.op.drop_column('users', 'object_sid')
