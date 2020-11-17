from opengever.base.sentry import log_msg_to_sentry
from opengever.core.upgrade import SchemaMigration
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


UNIT_ID_LENGTH = 30


members_table = table(
    "members",
    column("id"),
    column("admin_unit_id"),
)


committees_table = table(
    "committees",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
)


class AddAdminUnitToMember(SchemaMigration):
    """Add admin_unit column to Member.

    We apply a graceful strategy in case we find a deployment in invalid state.
    Instead of failing hard and blocking a potential upgrade path we migrate
    using a placeholder and notify that manual cleanup is needed. We don't
    expect any deployments in such state as it is currently not supported.
    """

    def migrate(self):
        self.add_admin_unit_column()
        self.migrate_data()
        self.make_admin_unit_column_non_nullable()

    def add_admin_unit_column(self):
        self.op.add_column(
            'members',
            Column('admin_unit_id', String(UNIT_ID_LENGTH), nullable=True)
        )

    def has_committees_for_multiple_admin_units(self):
        statement = select([committees_table.c.admin_unit_id]).distinct()
        results = list(self.execute(statement))
        return len(results) > 1

    def migrate_data(self):
        nof_members = self.execute(members_table.count()).scalar()
        # there are no members, this means that either the meeting feature
        # is not enabled, or not in use. no data migration is needed.
        if nof_members <= 0:
            return

        current_admin_unit_id = get_current_admin_unit().id()

        has_meeting_feature = api.portal.get_registry_record(
            'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled')
        # if we don't have the meeting feature active this means that another
        # admin-unit in the cluster has the meeting feature, but we are not
        # running schema migrations on that admin-unit.
        # this should not be the case at the moment as it is not yet officially
        # supported.
        # we gracefully continue with the upgrade and notify that manual
        # cleanup is needed.
        if not has_meeting_feature:
            log_msg_to_sentry(
                'Attempting to migrate members on {}, but meeting feature is '
                'not enabled. The admin_unit_id for members will be set to '
                '"FIXME". This MUST be cleaned up manually'.format(
                    current_admin_unit_id),
                request=self.portal.REQUEST)
            current_admin_unit_id = u'FIXME'
        # if we have committees on multiple admin-units in one cluster we
        # cannot reliably migrate members.
        # this should not be the case at the moment as it is not yet officially
        # supported.
        # we gracefully continue with the upgrade and notify that manual
        # cleanup is needed.
        if self.has_committees_for_multiple_admin_units():
            log_msg_to_sentry(
                'Attempting to migrate members, but found committees on '
                'multiple admin units. The admin_unit_id for members will be '
                'set to "FIXME". This MUST be cleaned up manually',
                request=self.portal.REQUEST)
            current_admin_unit_id = u'FIXME'

        self.execute(
            members_table.update().values(admin_unit_id=current_admin_unit_id)
        )

    def make_admin_unit_column_non_nullable(self):
        self.op.alter_column(
            'members', 'admin_unit_id', existing_type=String, nullable=False
        )
