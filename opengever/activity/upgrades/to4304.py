from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


class IncreaseActivityColumnLengths(SchemaMigration):
    """Increase lengths for several VARCHAR columns for 'activity' models in
    preparation for factoring out common column lengths to constants.
    """

    profileid = 'opengever.activity'
    upgradeid = 4304

    def migrate(self):
        self.increase_activity_kind_length()

    def increase_activity_kind_length(self):
        self.op.alter_column('activities',
                             'kind',
                             type_=String(255),
                             existing_nullable=False,
                             existing_type=String(50))
