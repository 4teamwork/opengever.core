from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestContactsVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestContactsVocabulary, self).setUp()

        self.peter_a = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'M\xfcller'))
        self.peter_b = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'Fl\xfcckiger'))
        self.meier_ag = create(Builder('organization')
                               .named(u'Meier AG'))
        self.teamwork_ag = create(Builder('organization')
                                  .named(u'4teamwork AG'))

        self.role1 = create(Builder('org_role')
                            .having(person=self.peter_a,
                                    organization=self.meier_ag,
                                    function='Developer'))
        self.role2 = create(Builder('org_role')
                            .having(person=self.peter_a,
                                    organization=self.teamwork_ag,
                                    function='Scheffe'))

    def test_contains_all_organizations_and_persons_and_org_roles(self):
        voca_factory = getUtility(IVocabularyFactory,
                                  name='opengever.contact.ContactsVocabulary')
        vocabulary = voca_factory(self.portal)

        self.assertTerms(
            [(self.peter_a, u'Peter M\xfcller'),
             (self.role1, u'Peter M\xfcller - Meier AG (Developer)'),
             (self.role2, u'Peter M\xfcller - 4teamwork AG (Scheffe)'),
             (self.peter_b, u'Peter Fl\xfcckiger'),
             (self.meier_ag, u'Meier AG'),
             (self.teamwork_ag, u'4teamwork AG')],
            vocabulary.search('*'))

    def test_supports_fuzzy_search(self):
        voca_factory = getUtility(IVocabularyFactory,
                                  name='opengever.contact.ContactsVocabulary')
        vocabulary = voca_factory(self.portal)

        self.assertTerms(
            [(self.meier_ag, 'Meier AG')],
            vocabulary.search('Meier'))

        self.assertTerms(
            [(self.peter_a, u'Peter M\xfcller'),
             (self.role1, u'Peter M\xfcller - Meier AG (Developer)'),
             (self.role2, u'Peter M\xfcller - 4teamwork AG (Scheffe)'),
             (self.peter_b, u'Peter Fl\xfcckiger')],
            vocabulary.search('Peter'))

        self.assertTerms(
            [(self.peter_b, u'Peter Fl\xfcckiger')],
            vocabulary.search('Peter Fl'))

        self.assertTerms(
            [(self.peter_b, u'Peter Fl\xfcckiger')],
            vocabulary.search('Pe Fl'))
