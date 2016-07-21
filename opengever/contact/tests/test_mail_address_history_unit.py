from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestAddressHistory(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_mail_addresses_histories(self):
        fritz = create(Builder('person')
                       .having(firstname=u'Fritz', lastname=u'M\xfcller'))

        home = create(Builder('mail_addresses_history')
                      .for_contact(fritz)
                      .labeled(u'Home')
                      .having(address=u'peter@example.com'))

        work = create(Builder('mail_addresses_history')
                      .for_contact(fritz)
                      .labeled(u'Work')
                      .having(address=u'm.peter@example.com'))

        self.assertEquals([home, work], fritz.mail_address_history)

    def test_organization_can_have_multiple_mail_addresses_histories(self):
        acme = create(Builder('organization')
                      .having(name=u'ACME'))

        sales = create(Builder('mail_addresses_history')
                       .for_contact(acme)
                       .labeled(u'Sales')
                       .having(address=u'sales@example.com'))

        hr = create(Builder('mail_addresses_history')
                    .for_contact(acme)
                    .labeled(u'HR')
                    .having(address=u'hr@example.com'))

        self.assertEquals([sales, hr], acme.mail_address_history)
