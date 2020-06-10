from opengever.core.upgrade import SchemaMigration


class DropImportStampColumnFromUserModel(SchemaMigration):
    """Drop import_stamp column from user model.
    """

    def migrate(self):
        self.op.drop_column('users', 'import_stamp')
