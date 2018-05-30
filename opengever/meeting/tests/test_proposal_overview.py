from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class TestProposalOverview(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_proposal_excerpt_document_link(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_word_proposal)
        agenda_item.decide()
        excerpt_document = agenda_item.generate_excerpt(title='The Excerpt')
        agenda_item.return_excerpt(excerpt_document)
        browser.open(self.submitted_word_proposal, view='tabbedview_view-overview')
        statusmessages.assert_no_error_messages()

        browser.css('#excerptBox a').first.click()
        statusmessages.assert_no_error_messages()

        self.assertEquals(excerpt_document.absolute_url(), browser.url)

    @browsing
    def test_no_proposal_excerpt_document_link_if_no_permission(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_word_proposal)
        agenda_item.decide()
        excerpt_document = agenda_item.generate_excerpt(title='The Excerpt')
        agenda_item.return_excerpt(excerpt_document)

        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_word_proposal, view='tabbedview_view-overview')
        statusmessages.assert_no_error_messages()
        self.assertEquals(excerpt_document.absolute_url(),
                          browser.css('#excerptBox a').first.attrib['href'])

        self.login(self.dossier_responsible, browser)
        self.meeting_dossier.__ac_local_roles_block__ = True
        self.meeting_dossier.reindexObjectSecurity()

        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_word_proposal, view='tabbedview_view-overview')
        statusmessages.assert_no_error_messages()
        with self.assertRaises(NoElementFound):
            browser.css('#excerptBox a').first.click()
