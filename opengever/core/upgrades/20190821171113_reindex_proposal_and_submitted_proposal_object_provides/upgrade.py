from ftw.upgrade import UpgradeStep


class ReindexProposalAndSubmittedProposalObjectProvides(UpgradeStep):
    """Reindex proposal and submitted proposal object provides.
    """

    def __call__(self):
        for proposal in self.objects(
                {'portal_type': ['opengever.meeting.proposal',
                                 'opengever.meeting.submittedproposal']},
                'Reindex object_provides for all proposal-ish.'):

            proposal.reindexObject(idxs=['object_provides'])
