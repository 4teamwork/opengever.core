from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.model import NotificationSetting
from opengever.activity.model import Watcher
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.globalindex.model.task import Task
from opengever.globalindex.model.task import TaskPrincipal
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.ogds.models.user import User
from opengever.ogds.models.user_settings import UserSettings
from opengever.usermigration.base import BaseUserMigration
from opengever.usermigration.exceptions import UserMigrationException
from operator import itemgetter
from sqlalchemy import select
from zope.sqlalchemy.datamanager import mark_changed
import logging


logger = logging.getLogger('opengever.usermigration')


class OGDSUserReferencesMigrator(BaseUserMigration):

    def __init__(self, portal, principal_mapping, mode='move'):
        super(OGDSUserReferencesMigrator, self).__init__(
            portal, principal_mapping, mode=mode
        )
        self.session = create_session()

        self.activity_actors_moved = []
        self.watcher_actors_moved = []
        self.notification_userids_moved = []
        self.notification_setting_userids_moved = []
        self.task_principals_moved = []
        self.task_issuers_moved = []
        self.task_responsibles_moved = []
        self.user_settings_moved = []
        self.favorites_moved = []
        self.reminders_moved = []
        self.secretaries_moved = []
        self.proposal_issuers_moved = []

    def _get_sql_rows_with_old_userid(self, table, column_name, old_userid):
        column = getattr(table.c, column_name)
        rows = self.session.execute(
            table.
            select().
            where(column == old_userid)
        ).fetchall()
        return rows

    def _migrate_sql_column(self, table, column_name, old_userid, new_userid):  # noqa
        moved = []

        rows_to_fix = self._get_sql_rows_with_old_userid(
            table, column_name, old_userid)

        if rows_to_fix:
            logger.info(
                "Migrating '{}.{}' ({} -> {})".format(
                    table.name, column_name, old_userid, new_userid))
            self._verify_user(new_userid)

            column = getattr(table.c, column_name)
            self.session.execute(
                table.update().
                where(column == old_userid).
                values(**{column_name: new_userid}))

            mark_changed(self.session)

            # Use primary key (possibly compound) as unique row identifier
            pk_cols = [c.name for c in table.primary_key]
            for row in rows_to_fix:
                pk = ['%s=%s' % (cn, getattr(row, cn, None)) for cn in pk_cols]
                row_id = '%s: ' % table.name + ','.join(pk)
                moved.append((row_id, old_userid, new_userid))
        return moved

    def migrate(self):
        existing_user_ids = map(
            itemgetter(0),
            self.session.execute(
                select([User.__table__.c.userid])).fetchall())

        for userid in existing_user_ids:
            if userid in self.principal_mapping:
                old_userid = userid
                new_userid = self.principal_mapping[old_userid]
                if new_userid not in existing_user_ids:
                    msg = "User '{}' not found in OGDS!".format(new_userid)
                    raise UserMigrationException(msg)

                # Migrate activity actors
                moved = self._migrate_sql_column(
                    Activity.__table__, 'actor_id',
                    old_userid, new_userid)
                self.activity_actors_moved.extend(moved)

                # Migrate notification userids
                moved = self._migrate_sql_column(
                    Notification.__table__, 'userid',
                    old_userid, new_userid)
                self.notification_userids_moved.extend(moved)

                # Migrate notification settings
                moved = self._migrate_sql_column(
                    NotificationSetting.__table__, 'userid',
                    old_userid, new_userid)
                self.notification_setting_userids_moved.extend(moved)

                # Migrate watcher actors
                moved = self._migrate_sql_column(
                    Watcher.__table__, 'actorid',
                    old_userid, new_userid)
                self.watcher_actors_moved.extend(moved)

                # Migrate task principals
                moved = self._migrate_sql_column(
                    TaskPrincipal.__table__, 'principal',
                    old_userid, new_userid)
                self.task_principals_moved.extend(moved)

                # Migrate task issuers
                moved = self._migrate_sql_column(
                    Task.__table__, 'issuer',
                    old_userid, new_userid)
                self.task_issuers_moved.extend(moved)

                # Migrate task responsibles
                moved = self._migrate_sql_column(
                    Task.__table__, 'responsible',
                    old_userid, new_userid)
                self.task_responsibles_moved.extend(moved)

                # Migrate user settings
                moved = self._migrate_sql_column(
                    UserSettings.__table__, 'userid',
                    old_userid, new_userid)
                self.user_settings_moved.extend(moved)

                # Migrate favorites
                moved = self._migrate_sql_column(
                    Favorite.__table__, 'userid',
                    old_userid, new_userid)
                self.favorites_moved.extend(moved)

                # Migrate task reminders
                moved = self._migrate_sql_column(
                    ReminderSetting.__table__, 'actor_id',
                    old_userid, new_userid)
                self.reminders_moved.extend(moved)

                # Migrate meeting secretary
                moved = self._migrate_sql_column(
                    Meeting.__table__, 'secretary_id',
                    old_userid, new_userid)
                self.secretaries_moved.extend(moved)

                # Migrate proposal issuer
                moved = self._migrate_sql_column(
                    Proposal.__table__, 'issuer',
                    old_userid, new_userid)
                self.proposal_issuers_moved.extend(moved)

        results = {
            'activity_actors': {
                'moved': self.activity_actors_moved,
                'copied': [],
                'deleted': []},
            'watcher_actors': {
                'moved': self.watcher_actors_moved,
                'copied': [],
                'deleted': []},
            'notification_userids': {
                'moved': self.notification_userids_moved,
                'copied': [],
                'deleted': []},
            'notification_setting_userids': {
                'moved': self.notification_setting_userids_moved,
                'copied': [],
                'deleted': []},
            'task_principals': {
                'moved': self.task_principals_moved,
                'copied': [],
                'deleted': []},
            'task_issuers': {
                'moved': self.task_issuers_moved,
                'copied': [],
                'deleted': []},
            'task_responsibles': {
                'moved': self.task_responsibles_moved,
                'copied': [],
                'deleted': []},
            'user_settings': {
                'moved': self.user_settings_moved,
                'copied': [],
                'deleted': []},
            'favorites': {
                'moved': self.favorites_moved,
                'copied': [],
                'deleted': []},
            'reminders': {
                'moved': self.reminders_moved,
                'copied': [],
                'deleted': []},
            'secretaries': {
                'moved': self.secretaries_moved,
                'copied': [],
                'deleted': []},
            'proposal_issuers': {
                'moved': self.proposal_issuers_moved,
                'copied': [],
                'deleted': []},
        }
        return results
