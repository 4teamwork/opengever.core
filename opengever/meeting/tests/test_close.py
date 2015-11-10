from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.meeting.model import Meeting
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
import transaction


class TestCloseMeeting(FunctionalTestCase):

    def setUp(self):
        super(TestCloseMeeting, self).setUp()
        self.repository_root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .within(self.repository_root))
        self.dossier = create(Builder('dossier')
                              .within(self.repository))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository))

        self.sablon_template = create(
            Builder('sablontemplate')
            .with_asset_file('excerpt_template.docx'))
        container = create(Builder('committee_container').having(
            excerpt_template=self.sablon_template))
        self.committee = create(Builder('committee').within(container))

        self.proposal_a = create(Builder('proposal')
                                 .titled(u'Proposal A')
                                 .within(self.dossier)
                                 .as_submitted()
                                 .having(committee=self.committee.load_model()))
        self.proposal_b = create(Builder('proposal')
                                 .titled(u'Proposal B')
                                 .within(self.dossier)
                                 .as_submitted()
                                 .having(committee=self.committee.load_model()))

        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model())
                              .scheduled_proposals([self.proposal_a, self.proposal_b])
                              .link_with(self.meeting_dossier))
        self.meeting.execute_transition('pending-held')

        # set correct public url, used for generated meeting urls
        get_current_admin_unit().public_url = self.portal.absolute_url()
        transaction.commit()

    @browsing
    def test_generate_excerpt_and_add_it_to_submittedproposal(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('#held-closed').first.click()

        submitted_proposal = self.proposal_a.load_model().resolve_sumitted_proposal()
        excerpt = submitted_proposal.listFolderContents()[0]
        self.assertEquals('Protocol Excerpt-barn-dec-13-2011',
                          excerpt.Title())
        self.assertEquals(u'protocol-excerpt-barn-dec-13-2011.docx',
                          excerpt.file.filename)

        generated_document = self.proposal_a.load_model().submitted_excerpt_document
        self.assertEquals(excerpt, generated_document.oguid.resolve_object())

    @browsing
    def test_excerpt_is_copied_to_proposal(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('#held-closed').first.click()

        excerpt = self.proposal_a.listFolderContents()[0]
        self.assertEquals('Protocol Excerpt-barn-dec-13-2011',
                          excerpt.Title())
        self.assertEquals(u'protocol-excerpt-barn-dec-13-2011.docx',
                          excerpt.file.filename)

        generated_document = self.proposal_a.load_model().excerpt_document
        self.assertEquals(excerpt, generated_document.oguid.resolve_object())

    @browsing
    def test_proposalhistory_is_added(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('#held-closed').first.click()

        browser.open(self.proposal_a, view=u'tabbedview_view-overview')
        entry = browser.css('.answer').first

        self.assertEquals('Proposal decided by Test User (test_user_1_)',
                          entry.css('h3').first.text)
        self.assertEquals('answer decided', entry.get('class'))

    @browsing
    def test_excerpt_is_displayed_in_proposal_view(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('#held-closed').first.click()

        generated_document = self.proposal_a.load_model().excerpt_document
        excerpt = generated_document.oguid.resolve_object()

        browser.open(self.proposal_a, view=u'tabbedview_view-overview')
        link = browser.css('#excerptBox a').first
        self.assertEquals(excerpt.absolute_url(), link.get('href'))
        self.assertEquals('Protocol Excerpt-barn-dec-13-2011', link.text)

    @browsing
    def test_states_are_updated(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('#held-closed').first.click()
        self.assertEquals('closed', Meeting.query.first().get_state().name)
        self.assertEquals('decided', self.proposal_a.get_state().name)

    @browsing
    def test_redirects_to_meeting_and_show_statusmessage(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('#held-closed').first.click()

        self.assertEquals(
            [u'The meeting B\xe4rn, Dec 13, 2011 has been successfully closed, '
             u'the excerpts have been generated and sent back to the '
             u'initial dossier.'],
            info_messages())

        self.assertEquals(self.meeting.get_url(), browser.url)
