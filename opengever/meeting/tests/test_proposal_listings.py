from copy import deepcopy
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


SUBMITTED_PROPOSAL = {
    'Decision number': '',
    'Meeting': '',
    'State': 'Submitted',
    'Comittee': u'Rechnungspr\xfcfungskommission',
    'Title': u'Vertr\xe4ge',
    'Description': u'F\xfcr weitere Bearbeitung bewilligen',
    'Date of submission': '31.08.2016',
    'Issuer': 'Ziegler Robert (robert.ziegler)'}

DRAFT_PROPOSAL = {
    'Decision number': '',
    'Meeting': '',
    'State': 'Pending',
    'Comittee': u'Kommission f\xfcr Verkehr',
    'Title': u'Antrag f\xfcr Kreiselbau',
    'Date of submission': '',
    'Issuer': 'Ziegler Robert (robert.ziegler)',
    'Description': ''}

DECIDED_PROPOSAL = {
    'Decision number': '2016 / 1',
    'Meeting': u'8. Sitzung der Rechnungspr\xfcfungskommission',
    'State': 'Decided',
    'Comittee': u'Rechnungspr\xfcfungskommission',
    'Title': u'Initialvertrag f\xfcr Bearbeitung',
    'Date of submission': '31.08.2016',
    'Issuer': 'Ziegler Robert (robert.ziegler)',
    'Description': ''}


def proposals_table(browser):
    return browser.css('table.listing').first


def proposal_dicts(browser):
    return proposals_table(browser).dicts()


def with_checkbox(expected_results):
    """In the default proposal listings we have to extend the expected
    results with the "checkbox"-row. These cells do not contain any text and
    are the first cells of the row.
    """
    results = []
    for expected_result in expected_results:
        result = {'': ''}
        result.update(expected_result)
        results.append(result)
    return results


class TestDossierProposalListing(IntegrationTestCase):

    features = ('meeting',)

    maxDiff = None

    @browsing
    def test_listing_shows_active_proposals_by_default(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEqual(with_checkbox([SUBMITTED_PROPOSAL, DRAFT_PROPOSAL]), proposal_dicts(browser))

    @browsing
    def test_listing_shows_translated_state(self, browser):
        # Switch to french to tests for encoding errors
        self.enable_languages()
        self.login(self.dossier_responsible, browser)
        browser.open()
        browser.click_on(u'Fran\xe7ais')
        browser.open(self.dossier, view='tabbedview_view-proposals', data={'proposal_state_filter': 'filter_proposals_all'})
        expected_proposals = [
            {
                u'Commission': u'Rechnungspr\xfcfungskommission',
                'Etat': 'Soumis',
                'Mandant': 'Ziegler Robert (robert.ziegler)',
                u'Num\xe9ro de d\xe9cision': '',
                u'S\xe9ance': '',
                'Soumis le': '31.08.2016',
                'Titre': u'Vertr\xe4ge',
                'Description': u'F\xfcr weitere Bearbeitung bewilligen',
            },
            {
                u'Commission': u'Kommission f\xfcr Verkehr',
                'Etat': 'En modification',
                'Mandant': 'Ziegler Robert (robert.ziegler)',
                u'Num\xe9ro de d\xe9cision': '',
                u'S\xe9ance': '',
                'Soumis le': '',
                'Titre': u'Antrag f\xfcr Kreiselbau',
                'Description': '',
            },
            {
                u'Commission': u'Rechnungspr\xfcfungskommission',
                'Etat': u'Cl\xf4tur\xe9',
                'Mandant': 'Ziegler Robert (robert.ziegler)',
                u'Num\xe9ro de d\xe9cision': '2016 / 1',
                u'S\xe9ance': u'8. Sitzung der Rechnungspr\xfcfungskommission',
                'Soumis le': '31.08.2016',
                'Titre': u'Initialvertrag f\xfcr Bearbeitung',
                'Description': '',
            },
        ]
        self.assertEqual(with_checkbox(expected_proposals), browser.css('.listing').first.dicts())

    @browsing
    def test_listing_only_shows_visible_proposals(self, browser):
        self.login(self.dossier_responsible, browser)

        self.draft_proposal.__ac_local_roles_block__ = True
        self.draft_proposal.reindexObject()

        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEqual(with_checkbox([SUBMITTED_PROPOSAL]), proposal_dicts(browser))

    @browsing
    def test_proposals_are_linked_correctly(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')

        first_link = proposals_table(browser).rows[1].css('a').first
        self.assertEqual(u'Vertr\xe4ge', first_link.text)

        expected_url = 'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/proposal-1'
        self.assertEqual(expected_url, first_link.get('href'))

    @browsing
    def test_proposals_are_linked_to_meeting_if_scheduled(self, browser):
        with self.login(self.committee_responsible):
            self.schedule_proposal(self.meeting, self.submitted_proposal)

        self.login(self.committee_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')

        expected_url = 'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view'
        elem = proposals_table(browser).rows[1].css('a.contenttype-opengever-meeting-meeting').first
        self.assertEqual(expected_url, elem.node.get('href'))

    @browsing
    def test_default_filter_hides_cancelled_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-cancel")
        browser.click_on("Confirm")
        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEqual(with_checkbox([SUBMITTED_PROPOSAL]), proposal_dicts(browser))

    @browsing
    def test_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-cancel")
        browser.click_on("Confirm")
        browser.open(self.dossier, view='tabbedview_view-proposals', data={'proposal_state_filter': 'filter_proposals_all'})
        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEqual(
            with_checkbox([SUBMITTED_PROPOSAL, cancelled_proposal, DECIDED_PROPOSAL]),
            proposal_dicts(browser))

    @browsing
    def test_decided_filter_shows_only_decided_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(
            self.dossier,
            view='tabbedview_view-proposals',
            data={'proposal_state_filter': 'filter_proposals_decided'},
        )
        self.assertEqual(with_checkbox([DECIDED_PROPOSAL]), proposal_dicts(browser))

    @browsing
    def test_decision_number_is_prefixed(self, browser):
        """When the word feature is enabled, the decision number is prefixed
        with the year of the meeting.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(
            self.dossier,
            view='tabbedview_view-proposals',
            data={'proposal_state_filter': 'filter_proposals_decided'},
        )
        proposal = deepcopy(DECIDED_PROPOSAL)
        proposal['Decision number'] = '2016 / 1'
        self.assertEqual(with_checkbox([proposal]), proposal_dicts(browser))

    @browsing
    def test_filtering_dossier_proposal_listing_by_name(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals', data={'searchable_text': u'f\xfcr Kreisel'})
        self.assertEqual(with_checkbox([DRAFT_PROPOSAL]), proposal_dicts(browser))


class TestMyProposals(IntegrationTestCase):

    features = ('meeting',)

    maxDiff = None

    @browsing
    def test_lists_only_proposals_issued_by_the_current_user(self, browser):
        REGULAR_USER_DRAFT_PROPOSAL = deepcopy(DRAFT_PROPOSAL)
        REGULAR_USER_DRAFT_PROPOSAL['Issuer'] = u'B\xe4rfuss K\xe4thi (kathi.barfuss)'

        with self.login(self.dossier_responsible):
            userid = self.regular_user.getId()
            self.draft_proposal.load_model().issuer = userid

        self.login(self.regular_user, browser)
        browser.open(view='tabbedview_view-myproposals')
        self.assertEqual([REGULAR_USER_DRAFT_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_listing_shows_active_proposals_by_default(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(view='tabbedview_view-myproposals')
        self.assertEqual([SUBMITTED_PROPOSAL, DRAFT_PROPOSAL],
                         proposal_dicts(browser))

    @browsing
    def test_decided_filter_shows_only_decided_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(view='tabbedview_view-myproposals', data={'proposal_state_filter': 'filter_proposals_decided'})
        self.assertEqual([DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-cancel")
        browser.click_on("Confirm")
        browser.open(view='tabbedview_view-myproposals', data={'proposal_state_filter': 'filter_proposals_all'})
        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEqual([SUBMITTED_PROPOSAL, cancelled_proposal, DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_filtering_my_proposal_listing_by_name(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(view='tabbedview_view-myproposals', data={'searchable_text': u'Vertr\xe4ge'})
        self.assertEqual([SUBMITTED_PROPOSAL], proposal_dicts(browser))


class TestSubmittedProposals(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_listing_shows_submitted_proposals_by_default(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')
        self.assertEqual([SUBMITTED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_proposals_are_linked_correctly_to_the_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')
        first_link = proposals_table(browser).rows[1].css('a').first
        self.assertEqual(u'Vertr\xe4ge', first_link.text)
        expected_url = 'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/submitted-proposal-1'
        self.assertEqual(expected_url, first_link.get('href'))

    @browsing
    def test_submitted_proposals_are_linked_to_meeting_if_scheduled(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')
        elem = proposals_table(browser).rows[1].css('a.contenttype-opengever-meeting-meeting').first
        expected_url = 'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view'
        self.assertEqual(expected_url, elem.node.get('href'))

    @browsing
    def test_listing_shows_active_proposals_by_default(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals')
        self.assertEqual([SUBMITTED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_decided_filter_shows_only_decided_proposals(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(
            self.committee,
            view='tabbedview_view-submittedproposals',
            data={'proposal_state_filter': 'filter_proposals_decided'},
        )
        self.assertEqual([DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_submitted_proposal_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-cancel")
        browser.click_on("Confirm")
        self.login(self.committee_responsible, browser)
        browser.open(
            self.committee,
            view='tabbedview_view-submittedproposals',
            data={'proposal_state_filter': 'filter_proposals_all'},
        )
        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEqual([SUBMITTED_PROPOSAL, DECIDED_PROPOSAL], proposal_dicts(browser))

    @browsing
    def test_filtering_submitted_proposal_listing_by_name(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-submittedproposals', data={'searchable_text': u'Vertr\xe4ge'})
        self.assertEqual([SUBMITTED_PROPOSAL], proposal_dicts(browser))
