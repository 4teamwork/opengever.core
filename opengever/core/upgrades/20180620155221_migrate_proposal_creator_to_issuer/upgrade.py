from ftw.upgrade import UpgradeStep


class MigrateProposalCreatorToIssuer(UpgradeStep):
    """Migrate proposal creator to issuer.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for proposal in self.objects(
                {'portal_type': ['opengever.meeting.proposal',
                                 'opengever.meeting.submittedproposal']},
                'Migrate proposal creator to issuer'):

            if not proposal.issuer:
                proposal.issuer = proposal.Creator()
