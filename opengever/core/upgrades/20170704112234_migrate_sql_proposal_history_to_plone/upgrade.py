from BTrees.OOBTree import OOBTree
from opengever.base.date_time import as_utc
from opengever.core.upgrade import SchemaMigration
from opengever.meeting.proposalhistory import ProposalHistory
from persistent.mapping import PersistentMapping
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import join
from sqlalchemy.sql.expression import table
from uuid import uuid4
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import logging


logger = logging.getLogger('opengever.upgrade')


proposalhistory_table = table(
    "proposalhistory",
    column("id"),
    column("proposal_id"),
    column("created"),
    column("userid"),
    column("text"),
    column("submitted_document_id"),
    column("document_title"),
    column("submitted_version"),
    column("meeting_id"),
    column("proposal_history_type"),
)

proposal_table = table(
    "proposals",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
    column("physical_path"),
    column("submitted_admin_unit_id"),
    column("submitted_int_id"),
    column("submitted_physical_path"),
)


class PropsosalHistoryEntryMigrator(object):
    """Migrate one proposal history entry."""

    polymorphic_identity_to_name = {
        'removescheduled': 'remove_scheduled',
        'documentsubmitted': 'document_submitted',
        'documentupdated': 'document_updated',
    }

    def __init__(self, row):
        """Row is a RowProxy with proposalhistory and proposal columns."""

        self.row = row
        self.intids = getUtility(IIntIds)

    def run(self):
        data = self.get_data()
        self.migrate_history_for_proposal(data)
        self.migrate_history_for_submitted_proposal(data)

    def get_data(self):
        """Build and return data dictionary.

        Beware, returns a dict, must be converted to PersistentMapping on
        store.
        """

        name = self.get_record_name()
        data = dict(created=self.get_timestamp(), userid=self.get_userid(),
                    name=name, uuid=uuid4())

        if name in ('scheduled', 'remove_scheduled'):
            meeting_id = self.get_meeting_id()
            if meeting_id:
                data['meeting_id'] = meeting_id

        if name in ('document_submitted', 'document_updated'):
            document_title = self.get_document_title()
            if document_title:
                data['document_title'] = document_title
            submitted_version = self.get_submitted_version()
            if submitted_version is not None:
                data['submitted_version'] = submitted_version

        return data

    def migrate_history_for_proposal(self, data):
        """Append record to proposals history."""

        proposal = self.get_proposal()
        if not proposal:
            return

        self.write_history_record(proposal, PersistentMapping(data))

    def migrate_history_for_submitted_proposal(self, data):
        """Append record to submitted proposals history, if required."""

        name = self.get_record_name()
        if name not in ('submitted', 'reopened', 'scheduled', 'decided',
                        'revised', 'remove_scheduled', 'document_submitted',
                        'document_updated'):
            return

        submitted_proposal = self.get_submitted_proposal()
        if not submitted_proposal:
            return

        self.write_history_record(submitted_proposal, PersistentMapping(data))

    def write_history_record(self, context, data):
        history = IAnnotations(context).setdefault(
            ProposalHistory.annotation_key, OOBTree())
        history[self.get_timestamp()] = data

    def get_record_name(self):
        """Return the name of the plone history record."""

        polymorphic_identity = self.row.proposal_history_type
        name = self.polymorphic_identity_to_name.get(
            polymorphic_identity, polymorphic_identity)
        return name

    def get_submitted_version(self):
        return self.row.submitted_version

    def get_document_title(self):
        return self.row.document_title

    def get_meeting_id(self):
        return self.row.meeting_id

    def get_userid(self):
        return self.row.userid

    def get_timestamp(self):
        return as_utc(self.row.created)

    def get_proposal(self):
        intid = self.row.int_id
        if intid is None:
            return None
        obj = self.intids.queryObject(intid)
        if obj is None:
            logger.warn('Missing proposal for int-id: {}'.format(
                intid))
        return obj

    def get_submitted_proposal(self):
        intid = self.row.submitted_int_id
        if intid is None:
            return None
        obj = self.intids.queryObject(intid)
        if obj is None:
            logger.warn('Missing submitted proposal for int-id: {}'.format(
                intid))
        return obj


class MigrateSQLProposalHistoryToPlone(SchemaMigration):
    """Migrate SQL proposal history to plone."""

    def migrate(self):
        self.check_precondition()
        self.migrate_data()
        self.drop_proposal_history_table()

    def has_proposals_for_multiple_admin_units(self):
        statement = select([proposal_table.c.admin_unit_id]).distinct()
        results = list(self.execute(statement))
        return len(results) > 1

    def check_precondition(self):
        proposals = self.execute(proposal_table.select()).fetchall()
        if proposals:
            msg = 'data migration supports only one admin-unit!'
            assert not self.has_proposals_for_multiple_admin_units(), msg

    def migrate_data(self):
        join_expr = join(
            proposalhistory_table, proposal_table,
            proposalhistory_table.c.proposal_id == proposal_table.c.id)
        statement = select(
            [proposalhistory_table, proposal_table]).select_from(join_expr)
        result_rows = self.execute(statement).fetchall()

        for result_row in result_rows:
            PropsosalHistoryEntryMigrator(result_row).run()

    def drop_proposal_history_table(self):
        self.op.drop_table('proposalhistory')
