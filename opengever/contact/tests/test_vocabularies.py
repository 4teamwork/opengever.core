from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.ogds.base.utils import ogds_service
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestContactsVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestContactsVocabulary, self).setUp()

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
        self.ogds_user = OgdsUserToContactAdapter(ogds_service().all_users()[0])

    def test_contains_only_active_organizations_and_persons_and_org_roles(self):
        voca_factory = getUtility(IVocabularyFactory,
                                  name='opengever.contact.ContactsVocabulary')
        vocabulary = voca_factory(self.portal)

        self.assertTerms(
            [(self.peter_a, u'Peter M\xfcller [1111]'),
             (self.role1, u'Peter M\xfcller [1111] - Meier AG (Developer)'),
             (self.role2, u'Peter M\xfcller [1111] - 4teamwork AG (Scheffe)'),
             (self.peter_b, u'Peter Fl\xfcckiger'),
             (self.meier_ag, u'Meier AG [2222]'),
             (self.teamwork_ag, u'4teamwork AG'),
             (self.ogds_user, u'Test User (test_user_1_)')],
            vocabulary.search('*'))

    def test_supports_fuzzy_search(self):
        voca_factory = getUtility(IVocabularyFactory,
                                  name='opengever.contact.ContactsVocabulary')
        vocabulary = voca_factory(self.portal)

        self.assertTerms(
            [(self.meier_ag, 'Meier AG [2222]')],
            vocabulary.search('Meier'))

        self.assertTerms(
            [(self.peter_a, u'Peter M\xfcller [1111]'),
             (self.role1, u'Peter M\xfcller [1111] - Meier AG (Developer)'),
             (self.role2, u'Peter M\xfcller [1111] - 4teamwork AG (Scheffe)'),
             (self.peter_b, u'Peter Fl\xfcckiger')],
            vocabulary.search('Peter'))

        self.assertTerms(
            [(self.peter_b, u'Peter Fl\xfcckiger')],
            vocabulary.search('Peter Fl'))

        self.assertTerms(
            [(self.peter_b, u'Peter Fl\xfcckiger')],
            vocabulary.search('Pe Fl'))

        self.assertTerms(
            [(self.peter_a, u'Peter M\xfcller [1111]'),
             (self.role1, u'Peter M\xfcller [1111] - Meier AG (Developer)'),
             (self.role2, u'Peter M\xfcller [1111] - 4teamwork AG (Scheffe)')],
            vocabulary.search('1111'))

        self.assertTerms(
            [(self.meier_ag, u'Meier AG [2222]')], vocabulary.search('2222'))
