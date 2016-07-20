from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import OrganizationHistory
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestPerson(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_organization_can_have_multiple_histories(self):
        organization = create(Builder('organization')
                              .having(name=u'ACME corporation'))

        history1 = create(Builder('organizationhistory')
                          .having(name=u'ACMOT corporation',
                                  contact=organization))
        history2 = create(Builder('organizationhistory')
                          .having(name=u'ACMTT corporation',
                                  contact=organization))

        self.assertEqual([history1, history2], organization.history)

    def test_is_contacthistory(self):
        organization = create(Builder('organization')
                              .having(name=u'ACME corporation'))
        history = create(Builder('organizationhistory')
                         .having(name=u'ACMOT corporation',
                                 contact=organization))

        self.assertTrue(isinstance(history, OrganizationHistory))
        self.assertEquals('organizationhistory', history.contact_history_type)
