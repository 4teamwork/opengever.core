from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.meeting.model import Meeting
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestMeetingQuery(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestMeetingQuery, self).setUp()

        self.committee = create(Builder('committee_model'))

    def test_all_upcoming_meetings_is_limited_by_committee(self):
        committee_2 = create(Builder('committee_model').having(int_id=5678))

        meeting1 = create(Builder('meeting')
                          .having(committee=self.committee,
                                  start=datetime.now() + timedelta(hours=1)))
        meeting2 = create(Builder('meeting')
                          .having(committee=self.committee,
                                  start=datetime.now() + timedelta(hours=1)))
        create(Builder('meeting')
               .having(committee=committee_2,
                       start=datetime.now() + timedelta(hours=1)))

        self.assertEquals([meeting1, meeting2],
                          Meeting.query.all_upcoming_meetings(self.committee))

    def test_all_upcoming_meetings_returns_only_future_meetings(self):
        create(Builder('meeting').having(committee=self.committee,
                                         start=datetime(2015, 01, 01)))
        meeting_1 = create(Builder('meeting')
                           .having(committee=self.committee,
                                   start=datetime(2015, 01, 10)))
        meeting_2 = create(Builder('meeting')
                           .having(committee=self.committee,
                                   start=datetime(2015, 01, 15)))

        with freeze(datetime(2015, 01, 10)):
            self.assertEquals(
                [meeting_1, meeting_2],
                Meeting.query.all_upcoming_meetings(self.committee))

    def test_get_next_meeting(self):
        create(Builder('meeting')
               .having(committee=self.committee, start=datetime(2015, 01, 01)))
        create(Builder('meeting')
               .having(committee=self.committee, start=datetime(2015, 01, 31)))
        create(Builder('meeting')
               .having(committee=self.committee, start=datetime(2015, 01, 25)))

        meeting = create(Builder('meeting')
                         .having(committee=self.committee,
                                 start=datetime(2015, 01, 10)))

        with freeze(datetime(2015, 01, 10)):
            self.assertEquals(meeting,
                              Meeting.query.get_next_meeting(self.committee))

    def test_get_last_meeting(self):
        create(Builder('meeting')
               .having(committee=self.committee, start=datetime(2015, 01, 01)))
        meeting = create(Builder('meeting')
               .having(committee=self.committee, start=datetime(2015, 01, 07)))
        create(Builder('meeting')
               .having(committee=self.committee, start=datetime(2015, 01, 15)))

        with freeze(datetime(2015, 01, 10)):
            self.assertEquals(meeting,
                              Meeting.query.get_last_meeting(self.committee))
