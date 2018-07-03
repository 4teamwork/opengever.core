from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text


class AddDescriptionColumnToAgendaItemAndProposal(SchemaMigration):
    """Add description column to agendaitems and proposals.
    """

    def migrate(self):
        self.op.add_column(
            'agendaitems',
            Column('description', Text))

        self.op.add_column(
            'proposals',
            Column('description', Text))

        self.op.add_column(
            'proposals',
            Column('submitted_description', Text))
