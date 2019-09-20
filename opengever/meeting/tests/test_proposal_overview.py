from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.testing import IntegrationTestCase
from urllib import urlencode


class TestProposalOverview(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_shows_discreet_transition_buttons_proposal_document_checked_out(self, browser):
        self.login(self.dossier_responsible, browser)

        doc = self.draft_proposal.get_proposal_document()
        self.checkout_document(doc)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')

        self.assertEqual(
            ['proposal-transition-cancel',
             'proposal-transition-submit',
             'Comment'],
            browser.css('.actionButtons .regular_buttons li').text
        )
        self.assertEqual(
            ['Comment'],
            browser.css('.actionButtons .regular_buttons li a').text
        )

    @browsing
    def test_shows_info_viewlet_message_proposal_document_checked_out(self, browser):
        self.login(self.dossier_responsible, browser)

        doc = self.draft_proposal.get_proposal_document()
        self.checkout_document(doc)

        browser.open(self.draft_proposal)

        self.assertEqual(
            ['The proposal document is being checked out by Ziegler Robert '
             '(robert.ziegler).'],
            info_messages())

    @browsing
    def test_shows_discreet_transition_button_committee_closed(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)
        editbar.menu_option('Actions', 'deactivate').click()

        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')

        self.assertEqual(
            ['proposal-transition-cancel',
             'proposal-transition-submit',
             'Comment'],
            browser.css('.actionButtons .regular_buttons li').text
        )
        self.assertEqual(
            ['proposal-transition-cancel', 'Comment'],
            browser.css('.actionButtons .regular_buttons li a').text
        )

    @browsing
    def test_shows_warning_message_committee_closed(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)
        editbar.menu_option('Actions', 'deactivate').click()

        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal)

        self.assertEqual(
            [u'The committee Kommission f\xfcr Verkehr is no longer active.'],
            warning_messages())

    @browsing
    def test_proposal_excerpt_document_link(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt_document = agenda_item.generate_excerpt(title='The Excerpt')
        agenda_item.return_excerpt(excerpt_document)

        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        statusmessages.assert_no_error_messages()
        expected_listing = [
            ['Title', u'Vertr\xe4ge'],
            ['Description', u'F\xfcr weitere Bearbeitung bewilligen'],
            ['Dossier', u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            ['Committee', u'Rechnungspr\xfcfungskommission'],
            ['Meeting', u'9. Sitzung der Rechnungspr\xfcfungskommission'],
            ['Issuer', 'Ziegler Robert (robert.ziegler)'],
            ['Proposal document', u'Vertr\xe4ge'],
            ['State', 'Decided'],
            ['Decision number', '2016 / 2'],
            ['Attachments', u'Vertr\xe4gsentwurf'],
            ['Excerpt', 'The Excerpt'],
        ]
        self.assertEqual(expected_listing, browser.css('table.listing').first.lists())

        browser.css('a.document_link')[2].click()
        statusmessages.assert_no_error_messages()
        self.assertEquals(excerpt_document.absolute_url(), browser.url)

    @browsing
    def test_no_proposal_excerpt_document_link_if_no_permission(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt_document = agenda_item.generate_excerpt(title='The Excerpt')
        agenda_item.return_excerpt(excerpt_document)

        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        statusmessages.assert_no_error_messages()
        self.assertEquals(excerpt_document.absolute_url(), browser.css('a.document_link')[2].attrib['href'])

        self.login(self.dossier_responsible, browser)
        self.meeting_dossier.__ac_local_roles_block__ = True
        self.meeting_dossier.reindexObjectSecurity()

        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        statusmessages.assert_no_error_messages()
        expected_listing = [
            ['Title', u'Vertr\xe4ge'],
            ['Description', u'F\xfcr weitere Bearbeitung bewilligen'],
            ['Dossier', u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            ['Committee', u'Rechnungspr\xfcfungskommission'],
            ['Meeting', u'9. Sitzung der Rechnungspr\xfcfungskommission'],
            ['Issuer', 'Ziegler Robert (robert.ziegler)'],
            ['Proposal document', u'Vertr\xe4ge'],
            ['State', 'Decided'],
            ['Decision number', '2016 / 2'],
            ['Attachments', u'Vertr\xe4gsentwurf'],
            ['Excerpt', 'The Excerpt'],
        ]
        self.assertEqual(expected_listing, browser.css('table.listing').first.lists())

    @browsing
    def test_webactions_are_shown_in_proposal_overview(self, browser):
        self.login(self.committee_responsible, browser)
        create(Builder('webaction')
               .titled(u'Action 1')
               .having(order=5,
                       display='action-buttons',
                       icon_name="fa-helicopter"))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=1,
                       display='action-buttons',
                       target_url="http://example.org/endpoint2"))

        browser.open(self.submitted_proposal, view='tabbedview_view-overview')

        webactions = browser.css('.webactions_buttons a.webaction_button')
        self.assertEquals(['Action 2', 'Action 1'], webactions.text)

        params = urlencode({'context': self.submitted_proposal.absolute_url(),
                            'orgunit': 'fa'})
        self.assertEqual(map(lambda item: item.get("href"), webactions),
                         ['http://example.org/endpoint2?{}'.format(params),
                          'http://example.org/endpoint?{}'.format(params)])

        self.assertEqual(
            map(lambda item: item.get("class"), webactions),
            ['webaction_button', 'webaction_button fa fa-helicopter'])

    @browsing
    def test_webactions_are_html_escaped(self, browser):
        self.login(self.regular_user, browser)

        create(Builder('webaction')
               .titled(u'<bold>Action with HTML</bold>')
               .having(display='action-buttons'))

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn('&lt;bold&gt;Action with HTML&lt;/bold&gt;',
                      browser.css('ul.webactions_buttons a').first.innerHTML)
