from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from opengever.usermigration.proposals import ProposalsMigrator


class TestProposalsMigrator(IntegrationTestCase):

    def setUp(self):
        super(TestProposalsMigrator, self).setUp()

        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

    def test_migrates_proposal_issuers(self):
        self.login(self.manager)

        ProposalsMigrator(
            self.portal,
            {self.dossier_responsible.getId(): 'hans.muster'},
            'move'
        ).migrate()

        self.assertEquals('hans.muster', self.proposal.issuer)
        self.assertEquals('hans.muster', self.submitted_proposal.issuer)
