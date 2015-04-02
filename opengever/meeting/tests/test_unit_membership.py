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

    def test_string_representation(self):
        membership = create(Builder('membership').having(
            committee=self.committee, member=self.member))

        expected = "<Membership u'Peter M\\xfcller' in u'\\xdcbungskommission' 2010-01-01:2014-01-01>"
        self.assertEqual(expected, str(membership))
        self.assertEqual(expected, repr(membership))

    def test_is_order_on_date_from_by_default(self):
        membership_1 = create(Builder('membership')
                              .having(member=self.member,
                                      committee=self.committee,
                                      date_from=date(2008, 01, 01),
                                      date_to=date(2015, 01, 01)))

        membership_2 = create(Builder('membership')
                              .having(member=self.member,
                                      committee=self.committee,
                                      date_from=date(1990, 01, 01),
                                      date_to=date(2000, 12, 31)))

        membership_3 = create(Builder('membership')
                              .having(member=self.member,
                                      committee=self.committee,
                                      date_from=date(2003, 01, 01),
                                      date_to=date(2007, 12, 31)))

        self.assertEqual(
            [membership_2, membership_3, membership_1],
            Membership.query.all())
