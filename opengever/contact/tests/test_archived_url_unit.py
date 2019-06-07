from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestArchivedURL(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_archived_urls(self):
        fritz = create(Builder('person')
                       .having(firstname=u'Fritz', lastname=u'M\xfcller'))

        home = create(Builder('archived_url')
                      .for_contact(fritz)
                      .labeled(u'ftw')
                      .having(url=u'http://www.example.com'))

        gever = create(Builder('archived_url')
                       .for_contact(fritz)
                       .labeled(u'gever')
                       .having(url=u'http://example.org'))

        self.assertEquals([home, gever], fritz.archived_urls)

    def test_organization_can_have_multiple_archived_urls(self):
        acme = create(Builder('organization')
                      .having(name=u'ACME'))

        info = create(Builder('archived_url')
                      .for_contact(acme)
                      .labeled(u'ftw')
                      .having(url=u'http://example.com'))

        gever = create(Builder('archived_url')
                       .for_contact(acme)
                       .labeled(u'gever')
                       .having(url=u'http://example.org'))

        self.assertEquals([info, gever], acme.archived_urls)
