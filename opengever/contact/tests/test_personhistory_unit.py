from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest2
from opengever.contact.models import ContactHistory


class TestPerson(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_person_can_have_multiple_histories(self):
        person = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'M\xfcller'))

        history1 = create(Builder('personhistory')
                          .having(firstname=u'Hans', lastname=u'M\xfcller',
                                  contact=person))
        history2 = create(Builder('personhistory')
                          .having(firstname=u'Fritz', lastname=u'M\xfcller',
                                  contact=person))

        self.assertEqual([history1, history2], person.history)

    def test_is_contacthistory(self):
        person = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'M\xfcller'))
        history = create(Builder('personhistory')
                         .having(firstname=u'Hans', lastname=u'M\xfcller',
                                 contact=person))

        self.assertTrue(isinstance(history, ContactHistory))
        self.assertEquals('personhistory', history.contact_history_type)
