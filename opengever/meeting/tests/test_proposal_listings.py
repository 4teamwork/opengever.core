from copy import deepcopy
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from copy import deepcopy


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

SUBMITTED_WORD_PROPOSAL = {
    'Decision number': '',
    'Meeting': '',
    'State': 'Submitted',
    'Comittee': u'Rechnungspr\xfcfungskommission',
    'Title': u'\xc4nderungen am Personalreglement',
    'Date of submission': '31.08.2016',
    'Issuer': 'Ziegler Robert (robert.ziegler)',
    'Description': ''}

DRAFT_WORD_PROPOSAL = {
    'Decision number': '',
    'Meeting': '',
    'State': 'Pending',
    'Comittee': u'Kommission f\xfcr Verkehr',
    'Title': u'\xdcberarbeitung der GAV',
    'Date of submission': '',
    'Issuer': 'Ziegler Robert (robert.ziegler)',
    'Description': ''}


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
    def test_listing_shows_translated_state(self, browser):
        # Switch to french to tests for encoding errors
        self.enable_languages()
        self.login(self.dossier_responsible, browser)
        browser.open()
        browser.click_on(u'Fran\xe7ais')

        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'proposal_state_filter': 'filter_proposals_all'})

        self.assertEquals(
            [{u'Comit\xe9': u'Rechnungspr\xfcfungskommission',
              'Etat': 'Soumis',
              'Mandant': 'Ziegler Robert (robert.ziegler)',
              u'Num\xe9ro de d\xe9cision': '',
              u'R\xe9union': '',
              'Soumis le': '31.08.2016',
              'Titre': u'Vertr\xe4ge',
              'Description': u'F\xfcr weitere Bearbeitung bewilligen'},
             {u'Comit\xe9': u'Kommission f\xfcr Verkehr',
              'Etat': 'En modification',
              'Mandant': 'Ziegler Robert (robert.ziegler)',
              u'Num\xe9ro de d\xe9cision': '',
              u'R\xe9union': '',
              'Soumis le': '',
              'Titre': u'Antrag f\xfcr Kreiselbau',
              'Description': ''},
             {u'Comit\xe9': u'Rechnungspr\xfcfungskommission',
              'Etat': u'Cl\xf4tur\xe9',
              'Mandant': 'Ziegler Robert (robert.ziegler)',
              u'Num\xe9ro de d\xe9cision': '2016 / 1',
              u'R\xe9union': u'8. Sitzung der Rechnungspr\xfcfungskommission',
              'Soumis le': '31.08.2016',
              'Titre': u'Initialvertrag f\xfcr Bearbeitung',
              'Description': ''},
             {u'Comit\xe9': u'Rechnungspr\xfcfungskommission',
              'Etat': 'Soumis',
              'Mandant': 'Ziegler Robert (robert.ziegler)',
              u'Num\xe9ro de d\xe9cision': '',
              u'R\xe9union': '',
              'Soumis le': '31.08.2016',
              'Titre': u'\xc4nderungen am Personalreglement',
              'Description': ''},
             {u'Comit\xe9': u'Kommission f\xfcr Verkehr',
              'Etat': 'En modification',
              'Mandant': 'Ziegler Robert (robert.ziegler)',
              u'Num\xe9ro de d\xe9cision': '',
              u'R\xe9union': '',
              'Soumis le': '',
              'Titre': u'\xdcberarbeitung der GAV',
              'Description': ''}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_proposals_are_linked_correctly(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbedview_view-proposals')

        first_link = proposals_table(browser).rows[1].css('a').first

        self.assertEquals(
            u'Vertr\xe4ge',
            first_link.text)
        self.assertEquals(
            'http://nohost/plone/ordnungssystem/fuhrung/'
            'vertrage-und-vereinbarungen/dossier-1/proposal-1',
            first_link.get('href'))

    @browsing
    def test_proposals_are_linked_to_meeting_if_scheduled(self, browser):
        with self.login(self.committee_responsible):
            self.schedule_proposal(self.meeting, self.submitted_proposal)

        self.login(self.committee_responsible, browser)
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
        browser.click_on('Cancel')
        browser.click_on("Confirm")

        browser.open(self.dossier, view='tabbedview_view-proposals')
        self.assertEquals(
            [SUBMITTED_PROPOSAL, SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_all_filter_shows_all_proposals(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Cancel')
        browser.click_on("Confirm")
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
    def test_decision_number_is_prefixed(self, browser):
        """When the word feature is enabled, the decision number is prefixed
        with the year of the meeting.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'proposal_state_filter': 'filter_proposals_decided'})

        proposal = deepcopy(DECIDED_PROPOSAL)
        proposal['Decision number'] = '2016 / 1'
        self.assertEquals([proposal], proposal_dicts(browser))

    @browsing
    def test_filtering_dossier_proposal_listing_by_name(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier,
                     view='tabbedview_view-proposals',
                     data={'searchable_text': u'\xdcberarbeitung'})

        self.assertEquals([DRAFT_WORD_PROPOSAL],
                          proposal_dicts(browser))


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
        self.assertEquals([REGULAR_USER_DRAFT_PROPOSAL], proposal_dicts(browser))

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
        browser.click_on('Cancel')
        browser.click_on("Confirm")
        browser.open(view='tabbedview_view-myproposals',
                     data={'proposal_state_filter': 'filter_proposals_all'})

        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEquals(
            [SUBMITTED_PROPOSAL, cancelled_proposal, DECIDED_PROPOSAL,
             SUBMITTED_WORD_PROPOSAL, DRAFT_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_filtering_my_proposal_listing_by_name(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(view='tabbedview_view-myproposals',
                     data={'searchable_text': u'\xc4nderungen'})

        self.assertEquals([SUBMITTED_WORD_PROPOSAL],
                          proposal_dicts(browser))


class TestSubmittedProposals(IntegrationTestCase):

    features = ('meeting',)

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
            u'Vertr\xe4ge',
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
        browser.click_on('Cancel')
        browser.click_on("Confirm")

        self.login(self.committee_responsible, browser)
        browser.open(self.committee,
                     view='tabbedview_view-submittedproposals',
                     data={'proposal_state_filter': 'filter_proposals_all'})

        cancelled_proposal = DRAFT_PROPOSAL.copy()
        cancelled_proposal['State'] = 'Cancelled'
        self.assertEquals(
            [SUBMITTED_PROPOSAL, DECIDED_PROPOSAL, SUBMITTED_WORD_PROPOSAL],
            proposal_dicts(browser))

    @browsing
    def test_filtering_submitted_proposal_listing_by_name(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee,
                     view='tabbedview_view-submittedproposals',
                     data={'searchable_text': u'Vertr\xe4ge'})

        self.assertEquals([SUBMITTED_PROPOSAL], proposal_dicts(browser))
