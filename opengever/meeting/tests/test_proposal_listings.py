from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class ProposalListingTests(FunctionalTestCase):

    def setUp(self):
        super(ProposalListingTests, self).setUp()

        self.dossier = create(Builder('dossier').titled(u'Dossier A'))
        self.committee = create(Builder('committee').titled('My committee'))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .titled(u'My Proposal')
                               .having(committee=self.committee.load_model(),
                                       initial_position=u'My p\xf6sition is',
                                       proposed_action=u'My proposed acti\xf6n'))


class TestDossierProposalListing(ProposalListingTests):

    @browsing
    def test_listing(self, browser):
        browser.login().open(self.dossier, view='tabbedview_view-proposals')
        table = browser.css('table.listing').first

        # TODO: state should be translated
        self.assertEquals(
            [{'State': 'pending',
              'Proposed action': u'My proposed acti\xf6n',
              'Initial Position': u'My p\xf6sition is',
              'Comittee': 'My committee',
              'Title': 'My Proposal'}],
            table.dicts())

    @browsing
    def test_proposals_are_linked_correctly(self, browser):
        browser.login().open(self.dossier, view='tabbedview_view-proposals')

        table = browser.css('table.listing').first
        link = table.rows[1].css('a').first

        self.assertEquals('My Proposal', link.text)
        self.assertEquals('http://example.com/dossier-1/proposal-1',
                          link.get('href'))


class TestSubmittedProposals(ProposalListingTests):

    def setUp(self):
        super(TestSubmittedProposals, self).setUp()

        self.submitted_proposal = create(Builder('submitted_proposal')
                                         .submitting(self.proposal))

    @browsing
    def test_listing(self, browser):
        browser.login().open(self.committee,
                             view='tabbedview_view-submittedproposals')
        table = browser.css('table.listing').first

        # TODO: state should be translated
        self.assertEquals(
            [{'State': 'submitted',
              'Proposed action': u'My proposed acti\xf6n',
              'Initial Position': u'My p\xf6sition is',
              'Comittee': 'My committee',
              'Title': 'My Proposal'}],
            table.dicts())

    @browsing
    def test_proposals_are_linked_correctly_to_the_submitted_proposal(self, browser):
        browser.login().open(self.committee,
                             view='tabbedview_view-submittedproposals')

        table = browser.css('table.listing').first
        link = table.rows[1].css('a').first

        self.assertEquals('My Proposal', link.text)
        self.assertEquals(
            'http://example.com/committee-1/submitted-proposal-1',
            link.get('href'))
