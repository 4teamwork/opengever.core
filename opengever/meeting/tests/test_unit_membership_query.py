from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.model import Membership
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitMembership(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMembership, self).setUp()
        self.session = self.layer.session

        self.member = create(Builder('member').having(lastname=u'M\xfcller'))
        self.committee = create(Builder('committee_model')
                                .having(title=u'\xdcbungskommission'))

    def setup_membership(self, date_from, date_to):
        return create(Builder('membership').having(
            committee=self.committee, member=self.member,
            date_from=date_from, date_to=date_to))

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
