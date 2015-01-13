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
        member = create(Builder('member').having(lastname=u'M\xfcller'))
        committee = create(Builder('committee_model')
                           .having(title=u'\xdcbungskommission'))
        membership = create(Builder('membership').having(
            committee=committee, member=member))

        expected = "<Membership u'Peter M\\xfcller' in u'\\xdcbungskommission' 2010-01-01:2014-01-01>"
        self.assertEqual(expected, str(membership))
        self.assertEqual(expected, repr(membership))
