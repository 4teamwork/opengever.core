from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitMembership(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMembership, self).setUp()
        self.session = self.layer.session

    def test_string_representation(self):
        member = create(Builder('member'))
        committee = create(Builder('committee_model'))
        membership = create(Builder('membership').having(
            committee=committee, member=member))

        expected = '<Membership "Peter Meier" in "Bar" 2010-01-01:2014-01-01>'
        self.assertEqual(expected, str(membership))
        self.assertEqual(expected, repr(membership))
