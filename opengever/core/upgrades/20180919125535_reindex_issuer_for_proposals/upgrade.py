from ftw.upgrade import UpgradeStep


class ReindexIssuerForProposals(UpgradeStep):
    """Reindex issuer for proposals.
    """

    def __call__(self):
        for proposal in self.objects(
                {'portal_type': ['opengever.meeting.proposal',
                                 'opengever.meeting.submittedproposal']},
                'Reindex proposal issuer'):

            proposal.reindexObject(idxs=['issuer'])
