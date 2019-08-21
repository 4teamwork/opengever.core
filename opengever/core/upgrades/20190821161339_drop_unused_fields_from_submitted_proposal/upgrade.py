from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import base_hasattr


REMOVED_FIELDS = ('relatedItems', 'predecessor_proposal')


class DropUnusedFieldsFromSubmittedProposal(UpgradeStep):
    """Drop unused fields from SubmittedProposal.
    """

    deferrable = True

    def __call__(self):
        for submitted_proposal in self.objects(
                {'portal_type': ['opengever.meeting.submittedproposal']},
                'Drop removed fields from submitted proposal.'):

            for field_name in REMOVED_FIELDS:
                if base_hasattr(submitted_proposal, field_name):
                    delattr(submitted_proposal, field_name)
