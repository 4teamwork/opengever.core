from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
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

    def test_meeting_title(self):
        self.assertEqual(
            u'Bern, Oct 18, 2013',
            Meeting(location=u'Bern', start=datetime(2013, 10, 18)).get_title())

        self.assertEqual(
            u'Oct 18, 2013',
            Meeting(start=datetime(2013, 10, 18)).get_title())

    @browsing
    def test_add_meeting(self, browser):
        browser.login().open(self.committee, view='add-meeting')
        browser.fill({
            'Start': datetime(2010, 1, 1, 10),
            'End': datetime(2010, 1, 1, 11),
            'Location': 'Somewhere',
        }).submit()

        self.assertEquals([u'Record created'], info_messages())

        committee_model = self.committee.load_model()
        self.assertEqual(1, len(committee_model.meetings))
        meeting = committee_model.meetings[0]

        self.assertEqual(datetime(2010, 1, 1, 10), meeting.start)
        self.assertEqual(datetime(2010, 1, 1, 11), meeting.end)
        self.assertEqual('Somewhere', meeting.location)

    @browsing
    def test_edit_meeting(self, browser):
        committee_model = self.committee.load_model()
        meeting = create(Builder('meeting')
                         .having(committee=committee_model,
                                 start=datetime(2013, 1, 1),
                                 location='There',))

        browser.login()
        browser.open(MeetingList.url_for(self.committee, meeting) + '/edit')
        browser.fill({'Start': datetime(2012, 5, 5, 15)}).submit()

        self.assertEquals([u'Changes saved'], info_messages())

        # refresh meeting, due to above request it has lost its session
        # this is expected behavior
        meeting = Meeting.query.get(meeting.meeting_id)
        self.assertEqual(datetime(2012, 5, 5, 15), meeting.start)
        self.assertEqual('There', meeting.location)
