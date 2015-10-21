from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


USER_ID_LENGTH = 255


class ReplaceNotificationsWatcherRelation(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4505

    def migrate(self):
        self.add_userid_column()
        self.migrate_data()
        self.remove_watcherid_column()
        self.make_userid_column_required()

        self.notifications_table = table(
            "notifications",
            column("id"),
            column("activity_id"),
            column("watcher_id"),
        )

    def add_userid_column(self):
        self.op.add_column('notifications', Column('userid', String(USER_ID_LENGTH)))

    def migrate_data(self):
        watcher_id_mapping = self.get_watcherid_userid_mapping()
        notifications_table = table(
            "notifications",
            column("id"),
            column("activity_id"),
            column("watcher_id"),
            column("userid")
        )

        notifications = self.connection.execute(
            notifications_table.select()).fetchall()
        for notification in notifications:
            userid = watcher_id_mapping[notification.watcher_id]
            self.execute(
                notifications_table.update()
                .values(userid=userid)
                .where(notifications_table.columns.id == notification.id)
            )

    def remove_watcherid_column(self):
        self.op.drop_column('notifications', 'watcher_id')

    def make_userid_column_required(self):
        self.op.alter_column('notifications', 'userid', nullable=False,
                             existing_type=String(USER_ID_LENGTH))

    def get_watcherid_userid_mapping(self):
        mapping = {}
        watchers_table = table(
            "watchers",
            column("id"),
            column("user_id")
        )

        watchers = self.connection.execute(watchers_table.select()).fetchall()
        for watcher in watchers:
            mapping[watcher.id] = watcher.user_id

        return mapping
