from opengever.core.upgrade import SchemaMigration


class RemoveAgendaItemTextFields(SchemaMigration):
    """Remove agenda item text fields.
    """

    def migrate(self):
        self.op.drop_column('agendaitems', 'discussion')
        self.op.drop_column('agendaitems', 'decision')
