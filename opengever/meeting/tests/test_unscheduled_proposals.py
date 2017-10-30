from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Meeting
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase


class TestUnscheduledProposals(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestUnscheduledProposals, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model())
                              .link_with(self.meeting_dossier))

        self.meeting_wrapper = MeetingWrapper.wrap(self.committee, self.meeting)

    def setup_proposal(self):
        root, folder = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(folder))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(committee=self.committee.load_model(),
                                  decision_draft=u'<div>Project allowed.</div>')
                          .as_submitted())

        return proposal

    def setup_proposal_agenda_item(self, browser):
        proposal = self.setup_proposal()
        proposal_model = proposal.load_model()

        browser.login().open(self.meeting.get_url())

        form = browser.css('#schedule_proposal').first
        form.fill({'proposal_id': str(proposal_model.proposal_id)}).submit()
        return proposal.load_model().agenda_item

    @browsing
    def test_list_unscheduled_proposals_returns_a_json_representation_for_all_unscheduled_proposals(self, browser):
        self.setup_proposal()
        self.setup_proposal()

        browser.login().open(self.meeting_wrapper, view='unscheduled_proposals')
        self.assertEquals(
            [{u'schedule_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/unscheduled_proposals/1/schedule',
              u'submitted_proposal_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/submitted-proposal-1',
              u'title': u'Fooo'},
             {u'schedule_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/unscheduled_proposals/2/schedule',
              u'submitted_proposal_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/submitted-proposal-2',
              u'title': u'Fooo'}],
            browser.json.get('items'))

    @browsing
    def list_only_unscheduled_proposals_are_listed(self, browser):
        proposal_a = self.setup_proposal()
        self.setup_proposal()

        self.meeting.schedule_proposal(proposal_a)

        browser.login().open(self.meeting_wrapper, view='unscheduled_proposals')
        self.assertEquals([], browser.json.get('items'))


class TestScheduleProposal(TestUnscheduledProposals):

    @browsing
    def test_schedules_proposal(self, browser):
        proposal = self.setup_proposal()

        view = 'unscheduled_proposals/{}/schedule'.format(
            proposal.load_model().proposal_id)
        browser.login().open(self.meeting_wrapper, view=view)

        agenda_items = Meeting.get(self.meeting.meeting_id).agenda_items
        self.assertEquals(1, len(agenda_items))
        self.assertTrue(agenda_items[0].has_proposal)
        self.assertEqual(proposal.load_model(), agenda_items[0].proposal)
        self.assertEqual([{u'messageTitle': u'Information',
                           u'message': u'Scheduled Successfully',
                           u'messageClass': u'info'}],
                         browser.json.get('messages'))

    @browsing
    def test_fills_decision_with_decision_draft_value(self, browser):
        proposal = self.setup_proposal()

        view = 'unscheduled_proposals/{}/schedule'.format(
            proposal.load_model().proposal_id)
        browser.login().open(self.meeting_wrapper, view=view)

        agenda_items = Meeting.get(self.meeting.meeting_id).agenda_items
        self.assertEquals(u'<div>Project allowed.</div>',
                          agenda_items[0].decision)

    @browsing
    def test_raise_forbidden_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        view = 'unscheduled_proposals/1/schedule'
        with browser.expect_http_error(code=403):
            browser.login().open(self.meeting_wrapper, view=view)

    @browsing
    def test_raise_notfound_with_invalid_proposal_id(self, browser):
        with browser.expect_http_error(reason='Not Found'):
            browser.login().open(self.meeting_wrapper,
                                 view='unscheduled_proposals/123/schedule')
