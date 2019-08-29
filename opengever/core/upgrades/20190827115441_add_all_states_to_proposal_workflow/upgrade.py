from DateTime import DateTime
from ftw.upgrade.helpers import update_security_for
from opengever.base.oguid import Oguid
from opengever.core.upgrade import SQLUpgradeStep
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


proposals_table = table(
    "proposals",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
    column("workflow_state"),
)

sql_to_plone_state_mapping = {
    "pending": "proposal-state-active",
    "submitted": "proposal-state-submitted",
    "scheduled": "proposal-state-scheduled",
    "decided": "proposal-state-decided",
    "cancelled": "proposal-state-cancelled",
}

wf_id = 'opengever_proposal_workflow'


class AddAllStatesToProposalWorkflow(SQLUpgradeStep):
    """Add all states to proposal workflow.

    If we switch away form `proposal-state-active` or if we switch
    to `proposal-state-active` we reindex security as all the other states have
    the same security settings.

    """
    def migrate(self):
        self.wf_tool = self.getToolByName('portal_workflow')

        self.install_upgrade_profile()

        for proposal in self.objects(
                {'portal_type': ['opengever.meeting.proposal']},
                'Set workflow state on plone proposal objects.'):
            self.set_new_proposal_workflow_state(proposal)

    def set_new_proposal_workflow_state(self, proposal):
        oguid = Oguid.for_object(proposal)

        row = self.execute(
                proposals_table.select()
                .where(proposals_table.c.admin_unit_id == oguid.admin_unit_id)
                .where(proposals_table.c.int_id == oguid.int_id)
            ).fetchone()
        model_state = row.workflow_state

        state_before = self.wf_tool.getStatusOf(wf_id, proposal)
        new_state = sql_to_plone_state_mapping[model_state]

        if new_state == state_before:
            return

        # The status is changed the same way as by WorkflowChainUpdater.
        self.wf_tool.setStatusOf(wf_id, proposal, {
            'review_state': new_state,
            'action': 'systemupdate',
            'actor': 'system',
            'comments': '',
            'time': DateTime()})
        proposal.reindexObject(idxs=['review_state'])

        # If we switch away from or to `proposal-state-active` we must
        # reindex security.
        if (state_before == 'proposal-state-active'
           or new_state == 'proposal-state-active'):
            update_security_for(proposal, reindex_security=True)
