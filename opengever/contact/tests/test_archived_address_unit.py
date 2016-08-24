from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestArchivedAddress(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_archived_addresses(self):
        person = create(Builder('person')
                        .having(firstname=u'Hans', lastname=u'M\xfcller'))

        address1 = create(Builder('archived_address')
                          .for_contact(person)
                          .labeled(u'Work')
                          .having(street=u'Dammweg 9', zip_code=u'3013',
                                  city=u'Bern'))
        address2 = create(Builder('archived_address')
                          .for_contact(person)
                          .labeled(u'Home')
                          .having(street=u'Musterstrasse 283',
                                  zip_code=u'1700',
                                  city=u'Fribourg'))

        self.assertEquals([address1, address2], person.archived_addresses)

    def test_organization_can_have_multiple_archived_addresses(self):
        acme = create(Builder('organization')
                      .having(name=u'ACME'))

        address1 = create(Builder('archived_address')
                          .for_contact(acme)
                          .labeled(u'Work')
                          .having(street=u'Dammweg 9', zip_code=u'3013',
                                  city=u'Bern'))
        address2 = create(Builder('archived_address')
                          .for_contact(acme)
                          .labeled(u'Home')
                          .having(street=u'Musterstrasse 283',
                                  zip_code=u'1700',
                                  city=u'Fribourg'))

        self.assertEquals([address1, address2], acme.archived_addresses)
