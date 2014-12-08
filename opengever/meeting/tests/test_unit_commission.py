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
        proposal = create(Builder('committee').having(title='Peter'))
        self.assertEqual('<Committee "Peter">', str(proposal))
        self.assertEqual('<Committee "Peter">', repr(proposal))
