from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import ArchivedContact
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestPerson(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_archived_contacts(self):
        person = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'M\xfcller'))

        archive1 = create(Builder('archived_person')
                          .having(firstname=u'Hans', lastname=u'M\xfcller',
                                  contact=person))
        archive2 = create(Builder('archived_person')
                          .having(firstname=u'Fritz', lastname=u'M\xfcller',
                                  contact=person))

        self.assertEqual([archive1, archive2], person.archived_contacts)

    def test_is_archived_contact(self):
        person = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'M\xfcller'))
        history = create(Builder('archived_person')
                         .having(firstname=u'Hans', lastname=u'M\xfcller',
                                 contact=person))

        self.assertTrue(isinstance(history, ArchivedContact))
        self.assertEquals('archived_person', history.archived_contact_type)
