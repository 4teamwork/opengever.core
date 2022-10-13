from opengever.base.model import is_oracle
from opengever.core.upgrade import SchemaMigration


class AddIndexForPredecessorId(SchemaMigration):
    """Add index for predecessor_id.
    """

    def migrate(self):
        if is_oracle():
            # The index already exists for Zug.
            return
        self.op.create_index('ix_tasks_predecessor_id', 'tasks', ['predecessor_id'])
