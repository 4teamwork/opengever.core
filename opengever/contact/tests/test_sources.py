from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.contact.sources import ContactsSource
from opengever.ogds.models.service import ogds_service
from opengever.testing import FunctionalTestCase


class TestContactsSource(FunctionalTestCase):

    def setUp(self):
        super(TestContactsSource, self).setUp()

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
