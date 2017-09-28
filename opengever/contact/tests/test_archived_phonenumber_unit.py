from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestArchviedPhoneNumber(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_archived_phonenumbers(self):
        fritz = create(Builder('person')
                       .having(firstname=u'Fritz', lastname=u'M\xfcller'))

        home = create(Builder('archived_phonenumber')
                      .for_contact(fritz)
                      .labeled(u'Home')
                      .having(phone_number=u'+41791234566'))

        work = create(Builder('archived_phonenumber')
                      .for_contact(fritz)
                      .labeled(u'Work')
                      .having(phone_number=u'0315110000'))

        self.assertEquals([home, work], fritz.archived_phonenumbers)

    def test_organization_can_have_multiple_archived_phonenumbers(self):
        acme = create(Builder('organization')
                      .having(name=u'ACME'))

        location1 = create(Builder('archived_phonenumber')
                           .for_contact(acme)
                           .labeled(u'Home')
                           .having(phone_number=u'+41791234566'))

        location2 = create(Builder('archived_phonenumber')
                           .for_contact(acme)
                           .labeled(u'Work')
                           .having(phone_number=u'0315110000'))

        self.assertEquals([location1, location2], acme.archived_phonenumbers)
