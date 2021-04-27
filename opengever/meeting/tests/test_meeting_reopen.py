from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.meeting.period import Period
from opengever.meeting.reopen import ReopenMeeting
from opengever.testing import IntegrationTestCase
import pytz


class TestReopenMeeting(IntegrationTestCase):

    features = ('meeting',)
    REOPEN_MEETING_ACTION = 'Reopen meeting'

    def test_reopen_held_meeting(self):
        self.login(self.committee_responsible)

        self.schedule_ad_hoc(self.meeting, 'Foo')
        self.schedule_paragraph(self.meeting, u'Para')
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal
        )
        agenda_item.decide()
        model = self.meeting.model
        period = Period.get_current(
            model.committee.resolve_committee(),
            model.start.date()
        )

        self.assertEqual(3, period.decision_sequence_number)
        self.assertEqual(2, period.meeting_sequence_number)
        self.assertEqual('held', model.workflow_state)
        self.assertEqual(
            ['pending', 'pending', 'decided'],
            [each.workflow_state for each in model.agenda_items]
        )
        self.assertEqual(
            [2, None, 3],
            [each.decision_number for each in model.agenda_items]
        )
        self.assertEqual(2, model.meeting_number)

        ReopenMeeting(model).reopen_meeting()

        self.assertEqual('pending', model.workflow_state)
        self.assertEqual(
            ['pending', 'pending', 'pending'],
            [each.workflow_state for each in model.agenda_items]
        )
        self.assertEqual(1, period.decision_sequence_number)
        self.assertEqual(1, period.meeting_sequence_number)

    def test_reopen_closed_meeting(self):
        self.login(self.committee_responsible)

        agenda_item = self.schedule_ad_hoc(self.meeting, 'Foo')
        self.schedule_paragraph(self.meeting, u'Para')
        agenda_item.decide()
        model = self.meeting.model
        model.close()
        period = Period.get_current(
            model.committee.resolve_committee(),
            model.start.date()
        )

        self.assertEqual(2, period.decision_sequence_number)
        self.assertEqual(2, period.meeting_sequence_number)
        self.assertEqual('closed', model.workflow_state)
        self.assertEqual(
            ['decided', 'pending'],  # the paragraph is always pending
            [each.workflow_state for each in model.agenda_items]
        )
        self.assertEqual(
            [2, None],
            [each.decision_number for each in model.agenda_items]
        )
        self.assertEqual(2, model.meeting_number)

        ReopenMeeting(model).reopen_meeting()

        self.assertEqual('pending', model.workflow_state)
        self.assertEqual(
            ['pending', 'pending'],
            [each.workflow_state for each in model.agenda_items]
        )
        self.assertEqual(1, period.decision_sequence_number)
        self.assertEqual(1, period.meeting_sequence_number)

    def test_error_invalid_meeting_state(self):
        self.login(self.committee_responsible)

        reopener = ReopenMeeting(self.meeting.model)
        self.assertEqual(
            [u"Can't reopen meeting in state 'pending'.",
             u"Unexpected state, can't reset meeting number."],
            reopener.get_errors()
        )

    def test_error_invalid_agenda_item_state(self):
        self.login(self.committee_responsible)

        agenda_item = self.schedule_ad_hoc(self.meeting, 'Foo')
        agenda_item.decide()
        agenda_item.decision_number = None

        reopener = ReopenMeeting(self.meeting.model)
        self.assertEqual(
            [u"Unexpected state, have agenda items but "
             u"can't reset decision number."],
            reopener.get_errors()
        )

    def test_error_newer_meetings_with_meeting_number_exist(self):
        self.login(self.committee_responsible)

        agenda_item = self.schedule_ad_hoc(self.meeting, 'Foo')
        self.schedule_paragraph(self.meeting, u'Para')
        agenda_item.decide()
        model = self.meeting.model
        model.close()

        meeting_dossier = create(
            Builder('meeting_dossier')
            .within(self.leaf_repofolder)
        )
        newer_meeting = create(
            Builder('meeting')
            .having(
                title=u'8. Sitzung der Rechnungspr\xfcfungskommission',
                committee=self.committee.load_model(),
                start=datetime(2016, 9, 12, 19, 30, tzinfo=pytz.UTC),
            )
            .link_with(meeting_dossier)
        )
        agenda_item = self.schedule_ad_hoc(newer_meeting, 'Foo')
        agenda_item.decide()

        reopener = ReopenMeeting(self.meeting.model)
        self.assertEqual(
            [u"The meetings '8. Sitzung der Rechnungspr\xfcfungskommission' "
             u"need to be reopened first."],
            reopener.get_errors()
        )

    @browsing
    def test_browser_reopen_meeting(self, browser):
        self.login(self.committee_responsible)

        self.schedule_ad_hoc(self.meeting, 'Foo')
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal
        )
        agenda_item.decide()
        model = self.meeting.model
        period = Period.get_current(
            model.committee.resolve_committee(),
            model.start.date()
        )

        self.assertEqual(3, period.decision_sequence_number)
        self.assertEqual(2, period.meeting_sequence_number)
        self.assertEqual('held', model.workflow_state)
        self.assertEqual(
            ['pending', 'decided'],
            [each.workflow_state for each in model.agenda_items]
        )
        self.assertEqual(
            [2, 3],
            [each.decision_number for each in model.agenda_items]
        )
        self.assertEqual(2, model.meeting_number)

        self.login(self.manager, browser)
        browser.open(model.get_url())
        editbar.menu_option('Actions', self.REOPEN_MEETING_ACTION).click()
        browser.find('Confirm').click()

        self.assertEqual([u"The meeting has been reopened."], info_messages())

        self.assertEqual('pending', model.workflow_state)
        self.assertEqual(
            ['pending', 'pending'],
            [each.workflow_state for each in model.agenda_items]
        )
        self.assertEqual(1, period.decision_sequence_number)
        self.assertEqual(1, period.meeting_sequence_number)

    @browsing
    def test_non_manager_cannot_reopen(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.meeting.model.get_url())
        self.assertNotIn(
            self.REOPEN_MEETING_ACTION, editbar.menu_options('Actions')
        )
        with browser.expect_unauthorized():
            browser.open(self.meeting.model.get_url(view='reopen_meeting'))
