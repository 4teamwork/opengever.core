from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Integer


class RenameActivityForeignKey(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4400

    def migrate(self):
        self.rename_notification_foreign_key()

    def rename_notification_foreign_key(self):
        fk_name = self.get_foreign_key_name('notifications', 'activiy_id')

        self.op.drop_constraint(fk_name, 'notifications', type_='foreignkey')
        self.op.alter_column('notifications',
                             'activiy_id',
                             new_column_name='activity_id',
                             existing_nullable=True,
                             existing_type=Integer)
        self.op.create_foreign_key(fk_name, 'notifications', 'activities',
                                   ['activity_id'], ['id'])
