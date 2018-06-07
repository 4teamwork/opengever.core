from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer


class AddTasktemplatePredecessorColumnToTaskModel(SchemaMigration):
    """Add tasktemplate_predecessor column to task model.
    """

    def migrate(self):
        self.op.add_column(
            'tasks',
            Column('tasktemplate_predecessor_id',
                   Integer, ForeignKey('tasks.id')))
