from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


# copied from opengever.globalindex.model.WORKFLOW_STATE_LENGTH
WORKFLOW_STATE_LENGTH = 255
DEFAULT_STATE_ID = 'active'


class AddWorkflowColumnToCommittteModel(SchemaMigration):
    """Add workflow column to Committte Model.
    """

    def migrate(self):
        self.add_workflow_state_column()
        self.insert_workflow_state()
        self.make_workflow_state_not_nullable()

    def add_workflow_state_column(self):
        self.op.add_column('committees',
                           Column('workflow_state',
                                  String(WORKFLOW_STATE_LENGTH),
                                  nullable=True))

    def insert_workflow_state(self):
        committees_table = table(
            'committees', column('id'), column('workflow_state'))

        self.execute(
            committees_table.update().values(workflow_state=DEFAULT_STATE_ID))

    def make_workflow_state_not_nullable(self):
        self.op.alter_column('committees', 'workflow_state',
                             existing_type=String(WORKFLOW_STATE_LENGTH),
                             nullable=False)
