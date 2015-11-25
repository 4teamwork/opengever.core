from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


# copied from opengever.globalindex.model.WORKFLOW_STATE_LENGTH
WORKFLOW_STATE_LENGTH = 255


class AddWorkflowStateToAgendaItem(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4624

    def migrate(self):
        self.add_workflow_state_column()
        self.insert_workflow_state_data()
        self.make_workflow_state()

    def add_workflow_state_column(self):
        self.op.add_column('agendaitems',
                           Column('workflow_state',
                                  String(WORKFLOW_STATE_LENGTH),
                                  nullable=True))

    def insert_workflow_state_data(self):
        agenda_items_table = table(
            'agendaitems',
            column('id'), column('workflow_state'), column('meeting_id'))
        self.execute(
            agenda_items_table.update().values(workflow_state='pending'))

        meeting_table = table('meetings',
                              column('id'), column('workflow_state'))

        for meeting in self.execute(
                meeting_table
                .select()
                .where(meeting_table.c.workflow_state == 'closed')):

            self.execute(agenda_items_table
                         .update()
                         .where(agenda_items_table.c.meeting_id == meeting.id)
                         .values(workflow_state='decided'))

    def make_workflow_state(self):
        self.op.alter_column('agendaitems', 'workflow_state',
                             existing_type=String(WORKFLOW_STATE_LENGTH),
                             nullable=False)
