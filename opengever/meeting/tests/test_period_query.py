from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.model import Period
from opengever.testing import MEMORY_DB_LAYER
from opengever.testing.helpers import localized_datetime
from unittest import TestCase


class TestPeriodQuery(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestPeriodQuery, self).setUp()

        self.committee = create(Builder('committee_model'))
        self.period = create(
            Builder('period').having(committee=self.committee,
                                     date_from=date(2010, 1, 1),
                                     date_to=date(2010, 12, 31)))

    def test_active_returns_only_active(self):
        create(Builder('period').having(workflow_state='closed',
                                        committee=self.committee,
                                        date_from=date(2010, 1, 1),
                                        date_to=date(2010, 12, 31)))

        self.assertEqual([self.period], Period.query.active().all())

    def test_by_committee_returns_periods_for_committee_in_all_states(self):
        committee_2 = create(Builder('committee_model').having(int_id=123))
        create(Builder('period').having(committee=committee_2,
                                        date_from=date(2010, 1, 1),
                                        date_to=date(2010, 12, 31)))

        period = create(Builder('period').having(workflow_state='closed',
                                                 committee=self.committee,
                                                 date_from=date(2010, 1, 1),
                                                 date_to=date(2010, 12, 31)))

        self.assertEqual([self.period, period],
                         Period.query.by_committee(self.committee).all())

    def test_get_current(self):
        create(Builder('period').having(workflow_state='closed',
                                        committee=self.committee,
                                        date_from=date(2010, 1, 1),
                                        date_to=date(2010, 12, 31)))

        self.assertEqual(self.period, Period.query.get_current(self.committee))

    def test_by_date_returns_all_periods_containing_date(self):
        period = create(Builder('period').having(committee=self.committee,
                                                 date_from=date(2010, 4, 1),
                                                 date_to=date(2010, 8, 31)))
        self.assertItemsEqual([self.period, period],
                              Period.query.by_date(date(2010, 5, 1)).all())

        self.assertItemsEqual([self.period],
                              Period.query.by_date(date(2010, 1, 1)).all())

    def test_get_for_meeting_filters_for_correct_committee(self):
        committee_2 = create(Builder('committee_model').having(int_id=123))
        create(Builder('period').having(committee=committee_2,
                                        date_from=date(2010, 1, 1),
                                        date_to=date(2010, 12, 31)))

        meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=localized_datetime(2010, 4, 1)))
        self.assertEqual(self.period, Period.query.get_for_meeting(meeting))

    def test_get_for_meeting_filters_for_correct_date(self):
        create(Builder('period').having(committee=self.committee,
                                        date_from=date(2011, 1, 1),
                                        date_to=date(2011, 12, 31)))

        meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=localized_datetime(2010, 4, 1)))
        self.assertEqual(self.period, Period.query.get_for_meeting(meeting))

    def test_get_for_meeting_returns_active_period_if_possible(self):
        closed_period = create(Builder('period').having(
            workflow_state='closed',
            committee=self.committee,
            date_from=date(2010, 6, 1),
            date_to=date(2011, 12, 31)))
        meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=localized_datetime(2010, 8, 1)))
        # Both periods match the date and committee of the meeting, but only
        # on is active
        self.assertEqual(self.period, Period.query.get_for_meeting(meeting))

        # Only the closed period matches the meeting date
        meeting.start = localized_datetime(2011, 8, 1)
        self.assertEqual(closed_period, Period.query.get_for_meeting(meeting))
