from opengever.core.upgrade import SchemaMigration


class RenameUniqueConstraints(SchemaMigration):
    """For Oracle compatibility the names of UniqueConstraints has to
    be limitted to max. 30 chars (see ORA-00972)."""

    profileid = 'opengever.meeting'
    upgradeid = 4215

    def migrate(self):
        self.remove_old_constraints()
        self.add_new_constraints()

    def remove_old_constraints(self):
        self.op.drop_constraint('ix_submitted_document_unique_target',
                                'submitteddocuments', type_='unique')

        self.op.drop_constraint('ix_submitted_document_unique_source',
                                'submitteddocuments', type_='unique')

    def add_new_constraints(self):
        self.op.create_unique_constraint(
            'ix_s_docs_unique_src',
            'submitteddocuments',
            ['admin_unit_id', 'int_id', 'proposal_id'])

        self.op.create_unique_constraint(
            'ix_s_docs_unique_dst',
            'submitteddocuments',
            ['submitted_admin_unit_id', 'submitted_int_id'])
