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
        self.meier_ag = create(Builder('organization')
                               .named(u'Meier AG')
                               .having(former_contact_id=2222))
        self.teamwork_ag = create(Builder('organization')
                                  .named(u'4teamwork AG'))
        self.school = create(Builder('organization')
                             .named(u'School')
                             .having(is_active=False))

        self.role1 = create(Builder('org_role')
                            .having(person=self.peter_a,
                                    organization=self.meier_ag,
                                    function='Developer'))
        self.role2 = create(Builder('org_role')
                            .having(person=self.peter_a,
                                    organization=self.teamwork_ag,
                                    function='Scheffe'))
        self.ogds_user = OgdsUserToContactAdapter(
            ogds_service().all_users()[0])

        self.source = ContactsSource(self.portal)

    def test_contains_only_active_organizations_and_persons_and_org_roles(self):
        self.assertTerms(
            [(self.peter_a, u'M\xfcller Peter [1111]'),
             (self.role1, u'M\xfcller Peter [1111] - Meier AG (Developer)'),
             (self.role2, u'M\xfcller Peter [1111] - 4teamwork AG (Scheffe)'),
             (self.peter_b, u'Fl\xfcckiger Peter'),
             (self.meier_ag, u'Meier AG [2222]'),
             (self.teamwork_ag, u'4teamwork AG'),
             (self.ogds_user, u'Test User (test_user_1_)')],
            self.source.search('*'))

    def test_supports_fuzzy_search(self):

        self.assertTerms(
            [(self.meier_ag, 'Meier AG [2222]')],
            self.source.search('Meier'))

        self.assertTerms(
            [(self.peter_a, u'M\xfcller Peter [1111]'),
             (self.role1, u'M\xfcller Peter [1111] - Meier AG (Developer)'),
             (self.role2, u'M\xfcller Peter [1111] - 4teamwork AG (Scheffe)'),
             (self.peter_b, u'Fl\xfcckiger Peter')],
            self.source.search('Peter'))

        self.assertTerms(
            [(self.peter_b, u'Fl\xfcckiger Peter')],
            self.source.search('Peter Fl'))

        self.assertTerms(
            [(self.peter_b, u'Fl\xfcckiger Peter')],
            self.source.search('Pe Fl'))

        self.assertTerms(
            [(self.peter_a, u'M\xfcller Peter [1111]'),
             (self.role1, u'M\xfcller Peter [1111] - Meier AG (Developer)'),
             (self.role2, u'M\xfcller Peter [1111] - 4teamwork AG (Scheffe)')],
            self.source.search('1111'))

        self.assertTerms(
            [(self.meier_ag, u'Meier AG [2222]')], self.source.search('2222'))
