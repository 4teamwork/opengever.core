from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.model import Membership
from opengever.testing import localized_datetime
from opengever.testing import MEMORY_DB_LAYER
from unittest import TestCase


class TestUnitMembershipQuery(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMembershipQuery, self).setUp()
        self.session = self.layer.session

        self.member = create(Builder('member').having(lastname=u'M\xfcller'))
        self.committee = create(Builder('committee_model')
                                .having(title=u'\xdcbungskommission'))

    def setup_membership(self, date_from, date_to,):
        return create(Builder('membership').having(
            committee=self.committee, member=self.member,
            date_from=date_from, date_to=date_to))

    def test_fetch_for_meeting(self):
        meeting = create(Builder('meeting').having(
                         committee=self.committee,
                         start=localized_datetime(2014, 7, 1),
                         end=None))
        create(Builder('membership').having(
            date_from=date(2013, 1, 1),
            date_to=date(2013, 12, 31),
            member=self.member,
            committee=self.committee))
        membership = create(Builder('membership').having(
            date_from=date(2014, 1, 1),
            date_to=date(2014, 12, 31),
            member=self.member,
            committee=self.committee))
        create(Builder('membership').having(
            date_from=date(2015, 1, 1),
            date_to=date(2015, 12, 31),
            member=self.member,
            committee=self.committee))

        self.assertEqual(
            membership,
            Membership.query.fetch_for_meeting(meeting, self.member))

    def test_only_active(self):
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)
        self.setup_membership(date(2010, 1, 1), yesterday)
        active = self.setup_membership(yesterday, tomorrow)
        self.assertEqual([active], Membership.query.only_active().all())

    def test_by_meeting(self):
        self.setup_membership(date(2004, 1, 20), date(2010, 1, 19))
        active = self.setup_membership(date(2010, 1, 20), date(2013, 7, 21))
        self.setup_membership(date(2013, 7, 22), date(2016, 1, 1))

        meeting = create(Builder('meeting').having(
                         committee=self.committee,
                         start=localized_datetime(2010, 1, 29),
                         end=None))

        self.assertEqual([active], Membership.query.for_meeting(meeting).all())

    def test_fetch_overlapping(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.fetch_overlapping(
            date(2012, 5, 10), date(2012, 7, 2), self.member, self.committee))

    def test_fetch_overlapping_ignore_id(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(None, Membership.query.fetch_overlapping(
            date(2012, 5, 10), date(2012, 7, 2),
            self.member, self.committee,
            ignore_id=membership.membership_id))

    def test_query_contained_within(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 5, 10), date(2012, 7, 2)).one())

    def test_query_contained_within_equal_start(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 5, 1), date(2012, 7, 2)).one())

    def test_query_contained_within_equal_end(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 5, 10), date(2012, 7, 10)).one())

    def test_query_contained_within_equal_start_and_end(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 5, 1), date(2012, 7, 10)).one())

    def test_query_overlaps_start(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 4, 30), date(2012, 5, 10)).one())

    def test_query_overlaps_end(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 5, 10), date(2012, 7, 20)).one())

    def test_query_overlaps_start_equal_end(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 4, 10), date(2012, 7, 10)).one())

    def test_query_overlaps_end_equal_start(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 5, 1), date(2012, 7, 28)).one())

    def test_query_overlaps_entire_period(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 3, 2), date(2012, 8, 2)).one())

    def test_query_equal_end_with_start(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 3, 2), date(2012, 5, 1)).one())

    def test_query_equal_start_with_end(self):
        membership = self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertEqual(membership, Membership.query.overlapping(
            date(2012, 7, 10), date(2012, 8, 1)).one())

    def test_query_ends_before(self):
        self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertIsNone(Membership.query.overlapping(
            date(2012, 3, 10), date(2012, 4, 30)).first())

    def test_query_starts_after(self):
        self.setup_membership(date(2012, 5, 1), date(2012, 7, 10))
        self.assertIsNone(Membership.query.overlapping(
            date(2012, 7, 11), date(2012, 9, 30)).first())
