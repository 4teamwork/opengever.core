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
