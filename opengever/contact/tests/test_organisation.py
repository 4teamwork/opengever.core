from opengever.contact.models import Contact
from opengever.contact.models import Organisation
from opengever.contact.models import URL
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestOrganisation(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_is_contact(self):
        organisation = Organisation(name='4teamwork AG')

        self.assertTrue(isinstance(organisation, Contact))
        self.assertEquals('organisation', organisation.contact_type)

    def test_organisation_can_have_multiple_urls(self):
        organisation = Organisation(name='4teamwork AG')

        info = URL(contact=organisation, url=u'http://www.4teamwork.ch')
        gever = URL(contact=organisation, url=u'http://www.onegovgever.ch')

        self.assertEquals([info, gever], organisation.urls)
        self.assertEquals([u'http://www.4teamwork.ch',
                           u'http://www.onegovgever.ch'],
                          [url.url for url in organisation.urls])
