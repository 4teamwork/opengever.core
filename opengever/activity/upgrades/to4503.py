from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.types import Enum


TASK_ISSUER_ROLE = 'task_issuer'
TASK_RESPONSIBLE_ROLE = 'task_responsible'
WATCHER_ROLE = 'regular_watcher'


class AddTableSubscriptions(SchemaMigration):
    """The n-n relationtable resources_watchers is replaced by an a new table
    `subscriptions` wich provides the additional attribute roles.

    The existing data in the `resource_watchers` table will be removed
    completly. The new table will be filled with a separate Upgradestep.

    This adjustment is introcued during the Release 4.6. development, but will
    be backported to 4.5 Release.
    """

    profileid = 'opengever.activity'
    upgradeid = 4503

    def migrate(self):
        self.add_subscriptions_table()
        self.remove_resource_watchers_table()

    def add_subscriptions_table(self):
        self.op.create_table(
            'subscriptions',
            Column('resource_id', Integer, primary_key=True),
            Column('watcher_id', Integer, primary_key=True),
            Column('role',
                   Enum(TASK_ISSUER_ROLE,
                        TASK_RESPONSIBLE_ROLE,
                        WATCHER_ROLE,
                        name='subscription_role_type'), primary_key=True)
        )

    def remove_resource_watchers_table(self):
        self.op.drop_table('resource_watchers')
