from opengever.activity.center import TASK_RESPONSIBLE_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text


DEFAULT_SETTINGS = {
    'task-added': [TASK_RESPONSIBLE_ROLE],
    'task-transition-reassign': [TASK_RESPONSIBLE_ROLE],
    'forwarding-transition-reassign-refused': [TASK_RESPONSIBLE_ROLE]
}


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
            Column('resource_id', Integer),
            Column('watcher_id', Integer),
            Column('roles', Text),
        )

    def remove_resource_watchers_table(self):
        self.op.drop_table('resource_watchers')
