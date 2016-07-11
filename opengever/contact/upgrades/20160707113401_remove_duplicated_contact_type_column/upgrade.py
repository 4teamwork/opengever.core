from opengever.core.upgrade import SchemaMigration


class RemoveDuplicatedContactTypeColumn(SchemaMigration):
    """Remove duplicated contact type column.
    """

    def migrate(self):
        self.op.drop_column('organizations', 'contact_type')
