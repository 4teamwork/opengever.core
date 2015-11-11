from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class DropMeetingStateHeld(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4616

    def migrate(self):
        self.migrate_held_state()

    def migrate_held_state(self):
        """The state held lost its relevance and is equivalent to pending.

        The migrations thus resets all meetings in the state held to the state
        pending.

        """
        meeting_table = table("meetings",
                              column("id"),
                              column("workflow_state"))

        self.execute(
            meeting_table.update()
                         .values(workflow_state='pending')
                         .where(meeting_table.c.workflow_state == 'held'))
