from datetime import date
from datetime import time
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.model import Meeting
from opengever.testing import FunctionalTestCase


class TestMeeting(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeeting, self).setUp()
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))

    @browsing
    def test_add_meeting(self, browser):
        browser.login().open(self.committee, view='add-meeting')
        browser.fill({
            'Date': '1/1/10',
            'Location': 'Somewhere',
            'Start time': '10:00 AM',
            'End time': '11:00 AM'
        }).submit()

        committee_model = self.committee.load_model()
        self.assertEqual(1, len(committee_model.meetings))
        meeting = committee_model.meetings[0]

        self.assertEqual(date(2010, 1, 1), meeting.date)
        self.assertEqual('Somewhere', meeting.location)
        self.assertEqual(time(10), meeting.start_time)
        self.assertEqual(time(11), meeting.end_time)

    @browsing
    def test_edit_meeting(self, browser):
        committee_model = self.committee.load_model()
        meeting = create(Builder('meeting')
                         .having(committee=committee_model,
                                 date=date(2013, 1, 1),
                                 location='There',))

        browser.login()
        browser.open(MeetingList.url_for(self.committee, meeting) + '/edit')
        browser.fill({'Date': '5/5/12', 'Start time': '3:00 PM'}).submit()

        # refresh meeting, due to above request it has lost its session
        # this is expected behavior
        meeting = Meeting.query.get(meeting.meeting_id)
        self.assertEqual(date(2012, 5, 5), meeting.date)
        self.assertEqual(time(15), meeting.start_time)
        self.assertEqual('There', meeting.location)
