from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestAddressHistory(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_phonenumberhistories(self):
        fritz = create(Builder('person')
                       .having(firstname=u'Fritz', lastname=u'M\xfcller'))

        home = create(Builder('phonenumberhistory')
                      .for_contact(fritz)
                      .labeled(u'Home')
                      .having(phone_number=u'+41791234566'))

        work = create(Builder('phonenumberhistory')
                      .for_contact(fritz)
                      .labeled(u'Work')
                      .having(phone_number=u'0315110000'))

        self.assertEquals([home, work], fritz.phonenumber_history)

    def test_organization_can_have_multiple_phonenumberhistories(self):
        acme = create(Builder('organization')
                      .having(name=u'ACME'))

        location1 = create(Builder('phonenumberhistory')
                           .for_contact(acme)
                           .labeled(u'Home')
                           .having(phone_number=u'+41791234566'))

        location2 = create(Builder('phonenumberhistory')
                           .for_contact(acme)
                           .labeled(u'Work')
                           .having(phone_number=u'0315110000'))

        self.assertEquals([location1, location2], acme.phonenumber_history)
