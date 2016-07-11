from opengever.core.upgrade import SchemaMigration


class RemoveDuplicatedDescriptionColumns(SchemaMigration):
    """Remove duplicated description columns.
    """

    def migrate(self):
        self.op.drop_column('persons', 'description')
        self.op.drop_column('organizations', 'description')
