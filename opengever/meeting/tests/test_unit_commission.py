from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitCommittee(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitCommittee, self).setUp()
        self.session = self.layer.session

    def test_string_representation(self):
        committee = create(Builder('committee_model')
                           .having(title=u'\xdcbungskommission'))
        self.assertEqual("<Committee u'\\xdcbungskommission'>", str(committee))
        self.assertEqual("<Committee u'\\xdcbungskommission'>", repr(committee))
