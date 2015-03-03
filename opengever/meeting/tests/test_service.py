from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.service import meeting_service
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestService(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestService, self).setUp()
        self.session = self.layer.session
        self.service = meeting_service()

    def test_all_committees(self):
        committee1 = create(Builder('committee_model'))
        committee2 = create(Builder('committee_model').having(int_id=5678))
        self.assertEqual([committee1, committee2],
                         self.service.all_committees())

    def test_all_committees_with_textfilter(self):
        committee1 = create(Builder('committee_model')
                            .having(title='Wasserkommission'))
        committee2 = create(Builder('committee_model')
                            .having(title='Kommission Recht und Wirtschaft',
                                    int_id=5678))

        self.assertEqual([committee1],
                         self.service.all_committees(text_filter='Wasser'))
        self.assertEqual([committee2],
                         self.service.all_committees(text_filter='Rech'))

    def test_fetch_committee_returns_correct_committee(self):
        create(Builder('committee_model'))
        committee2 = create(Builder('committee_model').having(int_id=5678))

        self.assertEqual(
            committee2,
            self.service.fetch_committee(committee2.committee_id))

    def test_fetch_committee_returns_none_for_invalid_id(self):
        self.assertIsNone(self.service.fetch_committee(1337))

    def test_get_upcoming_meetings_only_returns_meeting_for_the_given_committee(self):
        committee1 = create(Builder('committee_model'))
        committee2 = create(Builder('committee_model').having(int_id=5678))

        meeting1 = create(Builder('meeting')
                          .having(committee=committee1, date=date.today()))
        create(Builder('meeting')
               .having(committee=committee2, date=date.today()))
        meeting3 = create(Builder('meeting')
                          .having(committee=committee1, date=date.today()))

        self.assertEquals([meeting1, meeting3],
                          self.service.get_upcoming_meetings(committee1))

    def test_get_upcoming_meetings_only_returns_metting_in_the_future(self):
        committee1 = create(Builder('committee_model'))

        create(Builder('meeting').having(committee=committee1,
                                         date=date.today() - timedelta(days=1)))
        today = create(Builder('meeting')
                       .having(committee=committee1, date=date.today()))
        tomorrow = create(Builder('meeting')
                          .having(committee=committee1,
                                  date=date.today() + timedelta(days=1)))

        self.assertEquals([today, tomorrow],
                          self.service.get_upcoming_meetings(committee1))

    def test_get_next_meeting(self):
        committee = create(Builder('committee_model'))

        create(Builder('meeting')
               .having(committee=committee,
                       date=date.today() + timedelta(days=2)))

        create(Builder('meeting')
               .having(committee=committee,
                       date=date.today() + timedelta(days=1)))

        meeting3 = create(Builder('meeting')
                          .having(committee=committee,
                                  date=date.today()))

        self.assertEquals(meeting3, self.service.get_next_meeting(committee))

    def test_get_last_meeting(self):
        committee = create(Builder('committee_model'))

        create(Builder('meeting').having(committee=committee,
                                         date=date(2015, 01, 02)))

        create(Builder('meeting').having(committee=committee,
                                         date=date(2015, 02, 02)))

        meeting3 = create(Builder('meeting').having(committee=committee,
                                                    date=date(2015, 02, 15)))

        self.assertEquals(meeting3, self.service.get_last_meeting(committee))
