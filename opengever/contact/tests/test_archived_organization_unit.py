from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import ArchivedContact
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestPerson(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_organization_can_have_multiple_archived_contacts(self):
        organization = create(Builder('organization')
                              .having(name=u'ACME corporation'))

        archive1 = create(Builder('archived_organization')
                          .having(name=u'ACMOT corporation',
                                  contact=organization))
        archive2 = create(Builder('archived_organization')
                          .having(name=u'ACMTT corporation',
                                  contact=organization))

        self.assertEqual([archive1, archive2], organization.archived_contacts)

    def test_is_archived_contact(self):
        organization = create(Builder('organization')
                              .having(name=u'ACME corporation'))
        history = create(Builder('archived_organization')
                         .having(name=u'ACMOT corporation',
                                 contact=organization))

        self.assertTrue(isinstance(history, ArchivedContact))
        self.assertEquals('archived_organization', history.archived_contact_type)
