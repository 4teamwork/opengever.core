from opengever.base.oguid import Oguid
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


proposal_table = table(
    "proposals",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
    column("submitted_admin_unit_id"),
    column("submitted_int_id"),
    column("title"),
    column("legal_basis"),
    column("initial_position"),
    column("proposed_action"),
    column("considerations"),
    column("decision_draft"),
    column("publish_in"),
    column("disclose_to"),
    column("copy_for_attention"),
)


PROPOSAL_FIELDS = (
    'title',
    'legal_basis',
    'initial_position',
    'proposed_action',
    'decision_draft',
    'publish_in',
    'disclose_to',
    'copy_for_attention',
)

SUBMITTED_PROPOSAL_FIELDS = PROPOSAL_FIELDS + ('considerations',)


class MoveProposalFieldsToPloneObjects(SchemaMigration):
    """Move proposal fields to plone objects.
    """

    def migrate(self):
        self.migrate_data()
        self.drop_sql_columns()

    def has_proposals_for_multiple_admin_units(self):
        statement = select([proposal_table.c.admin_unit_id]).distinct()
        results = list(self.execute(statement))
        return len(results) > 1

    def migrate_data(self):
        proposals = self.execute(proposal_table.select()).fetchall()
        if proposals:
            msg = 'data migration supports only one admin-unit!'
            assert not self.has_proposals_for_multiple_admin_units(), msg

        for proposal in proposals:
            self.migrate_proposal_fields_to_plone_objects(proposal)

    def migrate_proposal_fields_to_plone_objects(self, sql_proposal):
        oguid = Oguid(sql_proposal.admin_unit_id, sql_proposal.int_id)
        proposal = oguid.resolve_object()
        for field_name in PROPOSAL_FIELDS:
            setattr(proposal, field_name, getattr(sql_proposal, field_name))

        submitted_oguid = Oguid(sql_proposal.submitted_admin_unit_id,
                                sql_proposal.submitted_int_id)
        submitted_proposal = submitted_oguid.resolve_object()
        if not submitted_proposal:
            return

        for field_name in SUBMITTED_PROPOSAL_FIELDS:
            setattr(submitted_proposal, field_name,
                    getattr(sql_proposal, field_name))

    def drop_sql_columns(self):
        for column_name in SUBMITTED_PROPOSAL_FIELDS:
            self.op.drop_column("proposals", column_name)
