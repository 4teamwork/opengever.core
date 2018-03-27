from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Meeting
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
import transaction


class TestHoldMeeting(FunctionalTestCase):

    def setUp(self):
        super(TestHoldMeeting, self).setUp()
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
            excerpt_template=self.sablon_template,
            protocol_template=self.sablon_template))
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

        # set correct public url, used for generated meeting urls
        get_current_admin_unit().public_url = self.portal.absolute_url()
        transaction.commit()

    def test_change_workflow_state(self):
        meeting = Meeting.query.first()
        meeting.hold()

        self.assertEquals('held', meeting.workflow_state)

    def test_generates_meeting_number(self):
        meeting = Meeting.query.first()
        meeting.hold()

        self.assertEquals(1, meeting.meeting_number)

    def test_generate_decision_numbers(self):
        Meeting.query.first().hold()

        item_a, item_b = AgendaItem.query.all()
        self.assertEquals(1, item_a.decision_number)
        self.assertEquals(2, item_b.decision_number)

    @browsing
    def test_hold_transition_is_not_visible(self, browser):
        browser.login().open(self.meeting.get_url())

        self.assertEquals(
            ['Close meeting'],
            browser.css('.actionButtons a').text)
