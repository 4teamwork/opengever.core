from opengever.base.interfaces import INoSeparateConnectionForSequenceNumbers
from opengever.base.security import elevated_privileges
from opengever.base.sentry import log_msg_to_sentry
from opengever.core.upgrade import SQLUpgradeStep
from plone import api
from plone.dexterity.utils import createContentInContainer
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.interface import alsoProvides
import logging


LOG = logging.getLogger('ftw.upgrade')


periods_table = table(
    'periods',
    column('id'),
    column('committee_id'),
    column('title'),
    column('date_from'),
    column('date_to'),
    column('decision_sequence_number'),
    column('meeting_sequence_number'),
)


# from opengever.meeting.period.PeriodValidator
def get_overlapping_periods(committee, start, end):
    query = {
        'portal_type': 'opengever.meeting.period',
        'start': {'query': end, 'range': 'max'},
        'end': {'query': start, 'range': 'min'},
        'path': '/'.join(committee.getPhysicalPath()),
    }
    catalog = api.portal.get_tool('portal_catalog')
    return catalog(query)


class MigratePeriodsFromSqlToPlone(SQLUpgradeStep):
    """Migrate periods from sql to plone.
    """

    def migrate(self):
        # do not open separate connections when increasing the sequence
        # number as that breaks atomicity of the upgrade and may cause
        # conflicts with the long-running upgrade transaction
        alsoProvides(self.portal.REQUEST,
                     INoSeparateConnectionForSequenceNumbers)

        query = {'portal_type': 'opengever.meeting.committee'}
        msg = 'Migrate periods from sql to plone'
        self._migrated_period_ids = []

        for committee in self.objects(query, msg):
            self.migrate_periods_for_committee(committee)

        LOG.info(u"Migrated {} periods with the following ids from sql to "
                  "plone: {}".format(
                    len(self._migrated_period_ids),
                    repr(self._migrated_period_ids)))

    def migrate_periods_for_committee(self, committee):
        committee_model = committee.load_model()

        periods_for_committee = self.execute(
            periods_table.select()
            .where(periods_table.c.committee_id == committee_model.committee_id)
        ).fetchall()

        # this is unexpected and wrong, but not wrong enough to completely
        # abort the upgrades. Periods can be created by the users manually.
        if not periods_for_committee:
            LOG.warning(u"No periods found for commitee {}".format(
                committee_model.title))
            return

        for period in periods_for_committee:
            self.create_plone_period(period, committee)
            self.drop_sql_period(period)

    def create_plone_period(self, period, committee):
        attributes = dict(
            title=period.title,
            start=period.date_from,
            end=period.date_to,
            decision_sequence_number=period.decision_sequence_number,
            meeting_sequence_number=period.meeting_sequence_number,
        )

        if get_overlapping_periods(committee, period.date_from, period.date_to):
            log_msg_to_sentry(
                'Overlapping period for {}. Upgrade will succeed but data '
                'needs to be fixed manually.'.format(period.title),
                context=committee,
                request=self.portal.REQUEST)

        with elevated_privileges():
            createContentInContainer(committee,
                                     'opengever.meeting.period',
                                     **attributes)

    def drop_sql_period(self, period):
        self.execute(
            periods_table.delete()
            .where(periods_table.c.id == period.id)
        )
        self._migrated_period_ids.append(period.id)
