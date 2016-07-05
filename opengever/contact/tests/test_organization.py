from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.contact.models import URL
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestOrganization(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_is_contact(self):
        organization = Organization(name='4teamwork AG')

        self.assertTrue(isinstance(organization, Contact))
        self.assertEquals('organization', organization.contact_type)

    def test_organization_can_have_multiple_urls(self):
        organization = Organization(name='4teamwork AG')

        info = URL(contact=organization, url=u'http://www.4teamwork.ch')
        gever = URL(contact=organization, url=u'http://www.onegovgever.ch')

        self.assertEquals([info, gever], organization.urls)
        self.assertEquals([u'http://www.4teamwork.ch',
                           u'http://www.onegovgever.ch'],
                          [url.url for url in organization.urls])
