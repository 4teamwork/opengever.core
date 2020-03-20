from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.vocabularies import ContactsVocabulary
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestContactVocabulary(FunctionalTestCase):
    use_default_fixture = False

    def key_value_provider(self):
        yield ('first-entry', 'First Entry')
        yield ('second-entry', 'Second Entry')
        yield ('third-entry', 'Third Entry')
        yield ('fourth-entry', 'Fourth Entry')
        yield ('fifth-entry', 'Fifth Entry')

    def test_custom_search_handle_each_word_seperatly(self):
        vocabulary = ContactsVocabulary.create_with_provider(self.key_value_provider)

        self.assertTermKeys(['first-entry'], vocabulary.search('fir en'))
        self.assertTermKeys(['first-entry'], vocabulary.search('en fir'))
        self.assertTermKeys(['third-entry'], vocabulary.search('ird'))

    def test_custom_search_can_handle_multiple_results(self):
        vocabulary = ContactsVocabulary.create_with_provider(self.key_value_provider)
        self.assertTermKeys(
            ['first-entry', 'second-entry', 'third-entry',
             'fourth-entry', 'fifth-entry', ],
            vocabulary.search('entry'))

        self.assertTermKeys(
            ['first-entry', 'fifth-entry'], vocabulary.search('fi en'))

    def test_custom_search_is_case_insensitive(self):
        vocabulary = ContactsVocabulary.create_with_provider(self.key_value_provider)

        self.assertTermKeys(['first-entry', ], vocabulary.search('FIR EN'))

    def test_custom_search_is_not_fuzzy(self):
        vocabulary = ContactsVocabulary.create_with_provider(self.key_value_provider)

        self.assertTermKeys([], vocabulary.search('firt'))

    def test_unicode_handling_in_vocabulary_search(self):

        def key_value_provider():
            yield (u'J\xf6rg R\xfctimann', u'j\xf6rg@r\xfctimann.\u0109h')

        vocabulary = ContactsVocabulary.create_with_provider(key_value_provider)

        self.assertTermKeys(
            [u'J\xf6rg R\xfctimann'],
            vocabulary.search("j"))


class TestAssignedClientsVocabularies(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestAssignedClientsVocabularies, self).setUp()
        admin_unit = create(Builder('admin_unit').as_current_admin_unit())
        user = create(Builder('ogds_user'))
        create(Builder('org_unit').id("client1")
               .having(admin_unit=admin_unit).as_current_org_unit()
               .assign_users([user]))
        create(Builder('org_unit').id("client2")
               .having(admin_unit=admin_unit))
        create(Builder('org_unit').id("client3")
               .having(admin_unit=admin_unit)
               .assign_users([user]))

    def test_contains_all_clients_assigned_to_the_current_client(self):
        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.AssignedClientsVocabulary')

        self.assertTermKeys(
            ['client1', 'client3'], voca_factory(self.portal))

    def test_other_assigned_vocabulary_does_not_include_the_current_client(self):
        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OtherAssignedClientsVocabulary')

        self.assertTermKeys(['client3'], voca_factory(self.portal))


class TestOrgUnitsVocabularyFactory(FunctionalTestCase):
    use_default_fixture = False

    def test_contains_all_org_units(self):
        admin_unit = create(Builder('admin_unit'))
        create(Builder('org_unit').id('rr')
               .having(title="Regierungsrat",
                       admin_unit=admin_unit))
        create(Builder('org_unit').id('arch')
               .having(title="Staatsarchiv",
                       admin_unit=admin_unit))
        create(Builder('org_unit').id('afi')
               .having(title="Informatikamt",
                       admin_unit=admin_unit))

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OrgUnitsVocabularyFactory')

        self.assertTermKeys(
            ['rr', 'arch', 'afi'], voca_factory(self.portal))

        self.assertTerms(
            [(u'afi', u'Informatikamt'),
             (u'rr', u'Regierungsrat'),
             (u'arch', u'Staatsarchiv')],
            voca_factory(self.portal))

    def test_contains_only_enabled_org_units(self):
        admin_unit = create(Builder('admin_unit'))
        create(Builder('org_unit').id('rr')
               .having(title="Regierungsrat",
                       admin_unit=admin_unit))
        create(Builder('org_unit').id('arch')
               .having(title="Staatsarchiv",
                       admin_unit=admin_unit))
        create(Builder('org_unit').id('afi')
               .having(title="Informatikamt",
                       admin_unit=admin_unit,
                       enabled=False))

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OrgUnitsVocabularyFactory')

        self.assertTermKeys(
            ['rr', 'arch'], voca_factory(self.portal))

        self.assertTerms(
            [(u'rr', u'Regierungsrat'),
             (u'arch', u'Staatsarchiv')],
            voca_factory(self.portal))

    def test_contains_hidden_org_units(self):
        admin_unit = create(Builder('admin_unit'))
        create(Builder('org_unit').id('rr')
               .having(title="Regierungsrat",
                       admin_unit=admin_unit))
        create(Builder('org_unit').id('arch')
               .having(title="Staatsarchiv",
                       admin_unit=admin_unit))
        create(Builder('org_unit').id('afi')
               .having(title="Informatikamt",
                       admin_unit=admin_unit,
                       hidden=True))

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OrgUnitsVocabularyFactory')

        self.assertTermKeys(
            ['rr', 'arch', 'afi'], voca_factory(self.portal))

        self.assertTerms(
            [(u'afi', u'Informatikamt'),
             (u'rr', u'Regierungsrat'),
             (u'arch', u'Staatsarchiv')],
            voca_factory(self.portal))
