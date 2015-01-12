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
            firstname=u'Peter', lastname=u'M\xfcller'))
        self.assertEqual("<Member u'Peter M\\xfcller'>", str(proposal))
        self.assertEqual("<Member u'Peter M\\xfcller'>", repr(proposal))
