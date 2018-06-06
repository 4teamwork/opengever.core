
from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import base_hasattr


PROPOSAL_FIELDS = (
    'copy_for_attention',
    'decision_draft',
    'disclose_to',
    'initial_position',
    'legal_basis',
    'proposed_action',
    'publish_in',
)

SUBMITTED_PROPOSAL_FIELDS = PROPOSAL_FIELDS + (
    'considerations',
)


class RemoveTextFieldsFormProposalsAndSubmittedProposals(UpgradeStep):
    """Remove text fields form proposals and submitted proposals.
    """

    def __call__(self):
        self.delete_proposal_fields()
        self.delete_submitted_proposal_fields()

    def delete_proposal_fields(self):
        for proposal in self.objects(
                {'portal_type': 'opengever.meeting.proposal'},
                'Delete proposal fields'):

            for field_name in PROPOSAL_FIELDS:
                if base_hasattr(proposal, field_name):
                    delattr(proposal, field_name)

    def delete_submitted_proposal_fields(self):
        for submitted_proposal in self.objects(
                {'portal_type': 'opengever.meeting.submittedproposal'},
                'Delete submitted proposal fields'):

            for field_name in SUBMITTED_PROPOSAL_FIELDS:
                if base_hasattr(submitted_proposal, field_name):
                    delattr(submitted_proposal, field_name)
