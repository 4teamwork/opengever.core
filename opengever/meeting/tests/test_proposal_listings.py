from copy import deepcopy
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


SUBMITTED_PROPOSAL = {
    'Reference Number': '1',
    'Decision number': '',
    'Meeting': '',
    'State': 'Submitted',
    'Comittee': u'Rechnungspr\xfcfungskommission',
    'Title': u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen'}

DRAFT_PROPOSAL = {
     'Reference Number': '2',
     'Decision number': '',
     'Meeting': '',
     'State': 'Pending',
     'Comittee': u'Kommission f\xfcr Verkehr',
     'Title': u'Antrag f\xfcr Kreiselbau'}

DECIDED_PROPOSAL = {
    'Reference Number': '3',
    'Decision number': '1',
    'Meeting': u'8. Sitzung der Rechnungspr\xfcfungskommission',
    'State': 'Decided',
    'Comittee': u'Rechnungspr\xfcfungskommission',
    'Title': u'Initialvertrag f\xfcr Bearbeitung'}

SUBMITTED_WORD_PROPOSAL = {
    'Reference Number': '4',
    'Decision number': '',
    'Meeting': '',
    'State': 'Submitted',
    'Comittee': u'Rechnungspr\xfcfungskommission',
    'Title': u'\xc4nderungen am Personalreglement'}

DRAFT_WORD_PROPOSAL = {
    'Reference Number': '5',
    'Decision number': '',
    'Meeting': '',
    'State': 'Pending',
    'Comittee': u'Kommission f\xfcr Verkehr',
    'Title': u'\xdcberarbeitung der GAV'}


def proposals_table(browser):
    return browser.css('table.listing').first


def proposal_dicts(browser):
    return proposals_table(browser).dicts()


class TestDossierProposalListing(IntegrationTestCase):
    features = ('meeting',)

    maxDiff = None

    @browsing
    def test_listing_shows_active_proposals_by_default(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEquals(
            [SUBMITTED_PROPOSAL, DRAFT_PROPOSAL,
             SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_proposals_are_linked_correctly(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')

        first_link = proposals_table(browser).rows[1].css('a').first

        self.assertEquals(
            u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen',
            first_link.text)
        self.assertEquals(
            'http://nohost/plone/ordnungssystem/fuhrung/'
            'vertrage-und-vereinbarungen/dossier-1/proposal-1',
            first_link.get('href'))

    @browsing
    def test_proposals_are_linked_to_meeting_if_scheduled(self, browser):
        with self.login(self.committee_responsible):
            self.schedule_proposal(self.meeting, self.submitted_proposal)

        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')

        elem = proposals_table(browser).rows[1].css(
            'a.contenttype-opengever-meeting-meeting').first
        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/'
            'committee-1/meeting-1/view',
            elem.node.get('href'))

    @browsing
    def test_default_filter_hides_cancelled_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.find('Cancel').click()

        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEquals(
            [SUBMITTED_PROPOSAL, SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.find('Cancel').click()
        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'proposal_state_filter': 'filter_proposals_all'})

        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEquals(
            [SUBMITTED_PROPOSAL, cancelled_proposal, DECIDED_PROPOSAL,
             SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_decided_filter_shows_only_decided_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'proposal_state_filter': 'filter_proposals_decided'})

        self.assertEquals([DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_decision_number_is_prefixed_when_word_feature_enabled(self, browser):
        """When the word feature is enabled, the decision number is prefixed
        with the year of the meeting.
        """
        self.activate_feature('word-meeting')
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'proposal_state_filter': 'filter_proposals_decided'})

        proposal = deepcopy(DECIDED_PROPOSAL)
        proposal['Decision number'] = '2016 / 1'
        self.assertEquals([proposal], proposal_dicts(browser))


class TestMyProposals(IntegrationTestCase):

    @browsing
    def test_lists_only_proposals_created_by_current_user(self, browser):
        with self.login(self.dossier_responsible):
            userid = self.regular_user.getId()
            self.draft_proposal.load_model().creator = userid

        self.login(self.regular_user, browser)
        browser.open(view='tabbedview_view-myproposals')
        self.assertEquals([DRAFT_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_listing_shows_active_proposals_by_default(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(view='tabbedview_view-myproposals')
        self.assertEquals(
            [SUBMITTED_PROPOSAL, DRAFT_PROPOSAL,
             SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_decided_filter_shows_only_decided_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(view='tabbedview_view-myproposals',
                     data={'proposal_state_filter': 'filter_proposals_decided'})

        self.assertEquals([DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.find('Cancel').click()
        browser.open(view='tabbedview_view-myproposals',
                     data={'proposal_state_filter': 'filter_proposals_all'})

        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEquals(
            [SUBMITTED_PROPOSAL, cancelled_proposal, DECIDED_PROPOSAL,
             SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))


class TestSubmittedProposals(IntegrationTestCase):

    @browsing
    def test_listing_shows_submitted_proposals_by_default(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')

        self.assertEquals(
            [SUBMITTED_PROPOSAL, SUBMITTED_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_proposals_are_linked_correctly_to_the_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')

        first_link = proposals_table(browser).rows[1].css('a').first

        self.assertEquals(
            u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen',
            first_link.text)
        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/'
            'committee-1/submitted-proposal-1',
            first_link.get('href'))

    @browsing
    def test_submitted_proposals_are_linked_to_meeting_if_scheduled(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_proposal)

        browser.open(self.committee, view='tabbedview_view-submittedproposals')

        elem = proposals_table(browser).rows[1].css(
            'a.contenttype-opengever-meeting-meeting').first
        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/'
            'committee-1/meeting-1/view',
            elem.node.get('href'))

    @browsing
    def test_listing_shows_active_proposals_by_default(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee,
                     view='tabbedview_view-submittedproposals')
        self.assertEquals(
            [SUBMITTED_PROPOSAL, SUBMITTED_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_decided_filter_shows_only_decided_proposals(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee,
                     view='tabbedview_view-submittedproposals',
                     data={'proposal_state_filter': 'filter_proposals_decided'})

        self.assertEquals([DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_submitted_proposal_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.find('Cancel').click()

        self.login(self.committee_responsible, browser)
        browser.open(self.committee,
                     view='tabbedview_view-submittedproposals',
                     data={'proposal_state_filter': 'filter_proposals_all'})

        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEquals(
            [SUBMITTED_PROPOSAL, DECIDED_PROPOSAL, SUBMITTED_WORD_PROPOSAL],
            proposal_dicts(browser))
