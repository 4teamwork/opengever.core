from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitCommission(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitCommission, self).setUp()
        self.session = self.layer.session

    def test_string_representation(self):
        proposal = create(Builder('commission').having(title='Peter'))
        self.assertEqual('<Commission "Peter">', str(proposal))
        self.assertEqual('<Commission "Peter">', repr(proposal))
