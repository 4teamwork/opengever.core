from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.contact.sources import ContactsSource
from opengever.ogds.models.service import ogds_service
from opengever.testing import FunctionalTestCase


class TestContactsSource(FunctionalTestCase):

    def setUp(self):
        super(TestContactsSource, self).setUp()

        self.peter_a = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'M\xfcller',
                                      former_contact_id=1111))
        self.peter_b = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'Fl\xfcckiger'))
        self.peter_c = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'Meier')
                              .having(is_active=False))
        self.ogds_user = OgdsUserToContactAdapter(
            ogds_service().all_users()[0])

        self.source = ContactsSource(self.portal)

    def test_getTermByToken_falls_back_to_ogds_user_if_not_contact_type_is_given(self):

        self.assertEqual(
            'ogds_user:test_user_1_',
            self.source.getTermByToken('ogds_user:test_user_1_').token
        )

        self.assertEqual(
            'ogds_user:test_user_1_',
            self.source.getTermByToken('test_user_1_').token
        )
