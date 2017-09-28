from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.model import Period
from opengever.testing import MEMORY_DB_LAYER
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
