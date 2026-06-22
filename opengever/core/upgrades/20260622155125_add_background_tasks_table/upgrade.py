from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text


class AddBackgroundTasksTable(SchemaMigration):

    def migrate(self):
        if u'background_tasks' in self.metadata.tables:
            return

        self.op.create_table(
            u'background_tasks',
            Column(u'task_id', String(36), primary_key=True),
            Column(u'admin_unit_id', String(30), nullable=False),
            Column(u'task_type', String(100), nullable=False),
            Column(u'status', String(20), nullable=False),
            Column(u'priority', Integer, nullable=False),
            Column(u'scheduled_for', DateTime, nullable=True),
            Column(u'created', DateTime, nullable=False),
            Column(u'started', DateTime, nullable=True),
            Column(u'finished', DateTime, nullable=True),
            Column(u'retries', Integer, nullable=False),
            Column(u'max_retries', Integer, nullable=False),
            Column(u'error_message', Text, nullable=True),
            Column(u'checkpoint_data', Text, nullable=True),
            Column(u'task_arguments', Text, nullable=True),
        )
