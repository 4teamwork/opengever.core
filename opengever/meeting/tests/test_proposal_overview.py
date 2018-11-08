from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class TestProposalOverview(IntegrationTestCase):

    features = ('meeting',)

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
