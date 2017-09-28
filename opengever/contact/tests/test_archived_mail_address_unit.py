from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestArchivedMailAddress(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_archived_mail_addresses(self):
        fritz = create(Builder('person')
                       .having(firstname=u'Fritz', lastname=u'M\xfcller'))

        home = create(Builder('archived_mail_addresses')
                      .for_contact(fritz)
                      .labeled(u'Home')
                      .having(address=u'peter@example.com'))

        work = create(Builder('archived_mail_addresses')
                      .for_contact(fritz)
                      .labeled(u'Work')
                      .having(address=u'm.peter@example.com'))

        self.assertEquals([home, work], fritz.archived_mail_addresses)

    def test_organization_can_have_multiple_archived_mail_addresses(self):
        acme = create(Builder('organization')
                      .having(name=u'ACME'))

        sales = create(Builder('archived_mail_addresses')
                       .for_contact(acme)
                       .labeled(u'Sales')
                       .having(address=u'sales@example.com'))

        hr = create(Builder('archived_mail_addresses')
                    .for_contact(acme)
                    .labeled(u'HR')
                    .having(address=u'hr@example.com'))

        self.assertEquals([sales, hr], acme.archived_mail_addresses)
