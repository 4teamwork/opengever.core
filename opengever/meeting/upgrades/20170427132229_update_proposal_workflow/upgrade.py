from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for
from plone import api


class UpdateProposalWorkflow(UpgradeStep):
    """Update proposal workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        map(self.update_object,
            self.objects({'portal_type': 'opengever.meeting.proposal'},
                         'Update proposal workflow security.'))

    def update_object(self, proposal):
        model = proposal.load_model()
        if model.get_state() == model.STATE_PENDING:
            update_security_for(proposal, reindex_security=False)
        else:
            api.content.transition(obj=proposal,
                                   to_state='proposal-state-submitted')
