from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


class IncreaseGlobalIndexColumnLengths(SchemaMigration):
    """Increase lengths for several VARCHAR columns in GlobalIndex in
    preparation for factoring out common column lengths to constants.
    """

    profileid = 'opengever.globalindex'
    upgradeid = 4301

    def migrate(self):
        self.increase_task_review_state_length()
        self.increase_task_responsible_length()
        self.increase_task_issuer_length()

    def increase_task_review_state_length(self):
        # Match WORKFLOW_STATE_LENGTH
        self.op.alter_column('tasks',
                             'review_state',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(50))

    def increase_task_responsible_length(self):
        # Match USER_ID_LENGTH
        self.op.alter_column('tasks',
                             'responsible',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(32))

    def increase_task_issuer_length(self):
        # Match USER_ID_LENGTH
        self.op.alter_column('tasks',
                             'issuer',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(32))
