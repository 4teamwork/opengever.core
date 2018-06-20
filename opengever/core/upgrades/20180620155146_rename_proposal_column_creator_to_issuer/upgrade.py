from opengever.core.upgrade import SchemaMigration


class RenameProposalColumnCreatorToIssuer(SchemaMigration):
    """Rename proposal column creator to issuer
    """

    def migrate(self):
        self.op.alter_column('proposals', 'creator',
                             new_column_name='issuer')
