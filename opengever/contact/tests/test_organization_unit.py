from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import Contact
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestOrganization(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_is_contact(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        self.assertTrue(isinstance(organization, Contact))
        self.assertEquals('organization', organization.contact_type)

    def test_organization_can_have_multiple_urls(self):
        organization = create(Builder('organization').named(u'4teamwork AG'))

        info = create(Builder('url')
                      .for_contact(organization)
                      .labeled(u'Info')
                      .having(url=u'http://www.4teamwork.ch'))

        gever = create(Builder('url')
                       .for_contact(organization)
                       .labeled(u'Info')
                       .having(url=u'http://www.onegovgever.ch'))

        self.assertEquals([info, gever], organization.urls)
        self.assertEquals([u'http://www.4teamwork.ch',
                           u'http://www.onegovgever.ch'],
                          [url.url for url in organization.urls])
