from copy import deepcopy
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


ALL_PROPOSALS = [
    {'Reference Number': '1',
     'Meeting': '',
     'State': 'Submitted',
     'Comittee': u'Rechnungspr\xfcfungskommission',
     'Title': u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen'},
    {'Reference Number': '2',
     'Meeting': '',
     'State': 'Pending',
     'Comittee': u'Kommission f\xfcr Verkehr',
     'Title': u'Antrag f\xfcr Kreiselbau'},
    {'Reference Number': '3',
     'Meeting': '',
     'State': 'Submitted',
     'Comittee': u'Rechnungspr\xfcfungskommission',
     'Title': u'\xc4nderungen am Personalreglement'},
    {'State': 'Pending',
     'Reference Number': '4',
     'Comittee': u'Kommission f\xfcr Verkehr',
     'Title': u'\xdcberarbeitung der GAV',
     'Meeting': ''},
]

SUBMITTED_PROPOSALS = [
    {'Reference Number': '1',
     'Meeting': '',
     'State': 'Submitted',
     'Comittee': u'Rechnungspr\xfcfungskommission',
     'Title': u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen'},
    {'Reference Number': '3',
     'Meeting': '',
     'State': 'Submitted',
     'Comittee': u'Rechnungspr\xfcfungskommission',
     'Title': u'\xc4nderungen am Personalreglement'},
]


def proposals_table(browser):
    return browser.css('table.listing').first


def proposal_dicts(browser):
    return proposals_table(browser).dicts()


class TestDossierProposalListing(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_listing(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEquals(ALL_PROPOSALS, proposal_dicts(browser))

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

        expected = deepcopy(ALL_PROPOSALS)
        expected[0]['Meeting'] = u'9. Sitzung der Rechnungspr\xfcfungskommission'
        expected[0]['State'] = u'Scheduled'
        self.assertEquals(expected, proposal_dicts(browser))

    @browsing
    def test_only_shows_active_proposals_by_default(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.find('Cancel').click()

        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEquals(
            ALL_PROPOSALS[:1] + ALL_PROPOSALS[2:],
            proposal_dicts(browser))

    @browsing
    def test_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.find('Cancel').click()
        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'proposal_state_filter': 'filter_all'})

        expected = deepcopy(ALL_PROPOSALS)
        expected[1]['State'] = 'Cancelled'
        self.assertEquals(expected, proposal_dicts(browser))


class TestMyProposals(IntegrationTestCase):

    @browsing
    def test_lists_only_proposals_created_by_current_user(self, browser):
        with self.login(self.dossier_responsible):
            userid = self.regular_user.getId()
            self.draft_proposal.load_model().creator = userid

        self.login(self.regular_user, browser)
        browser.open(view='tabbedview_view-myproposals')
        self.assertEquals(ALL_PROPOSALS[1:2], proposal_dicts(browser))


class TestSubmittedProposals(IntegrationTestCase):

    @browsing
    def test_listing(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')

        self.assertEquals(SUBMITTED_PROPOSALS, proposal_dicts(browser))

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

        expected = deepcopy(SUBMITTED_PROPOSALS)
        expected[0]['Meeting'] = u'9. Sitzung der Rechnungspr\xfcfungskommission'
        expected[0]['State'] = u'Scheduled'
        self.assertEquals(expected, proposal_dicts(browser))
