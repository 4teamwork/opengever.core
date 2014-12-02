from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitMember(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMember, self).setUp()
        self.session = self.layer.session

    def test_string_representation(self):
        proposal = create(Builder('member').having(
            firstname='Peter', lastname="Meier"))
        self.assertEqual('<Member "Peter Meier">', str(proposal))
        self.assertEqual('<Member "Peter Meier">', repr(proposal))
