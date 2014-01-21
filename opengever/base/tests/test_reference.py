from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.testing import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryAdapter


class TestLocalReferenceNumber(FunctionalTestCase):

    def test_plone_site_returns_client_id(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        proxy.client_id = u'FAKE CLIENT'

        self.assertEquals(
            u'FAKE CLIENT', IReferenceNumber(self.portal).get_local_number())

    def test_repository_root_returns_empty_string(self):
        root = create(Builder('repository_root'))

        self.assertEquals(
            '', IReferenceNumber(root).get_local_number())

    def test_repositoryfolder_returns_reference_prefix_of_the_context(self):
        repository = create(Builder('repository')
                            .having(reference_number_prefix=u'5'))

        self.assertEquals(
            u'5', IReferenceNumber(repository).get_local_number())

    def test_dossier_returns_reference_prefix_of_the_context(self):
        dossier = create(Builder('dossier'))

        IReferenceNumberPrefix(self.portal).set_number(dossier, number=u'7')

        self.assertEquals(
            u'7', IReferenceNumber(dossier).get_local_number())


class TestReferenceNumberAdapter(FunctionalTestCase):

    def setUp(self):
        super(TestReferenceNumberAdapter, self).setUp()

        root = create(Builder('repository_root'))
        repo_2 = create(Builder('repository')
                        .within(root)
                        .having(reference_number_prefix=u'2'))
        repo_2_4 = create(Builder('repository')
                          .within(repo_2)
                          .having(reference_number_prefix=u'4'))
        repo_2_4_7 = create(Builder('repository')
                            .within(repo_2_4)
                            .having(reference_number_prefix=u'7'))
        dossier = create(Builder('dossier').within(repo_2_4_7))
        IReferenceNumberPrefix(repo_2_4_7).set_number(dossier, number=u'8')

        self.subdossier = create(Builder('dossier').within(dossier))
        IReferenceNumberPrefix(dossier).set_number(self.subdossier, number=u'2')

    def test_returns_full_number_for_the_context(self):

        self.assertEquals(
            {'site': [u'OG', ],
             'repositoryroot': [''],
             'repository': [u'2', u'4', u'7'],
             'dossier': [u'8', u'2']},
            IReferenceNumber(self.subdossier).get_parent_numbers())

    def test_use_dotted_as_default_formatter(self):
        self.assertEquals(
            'OG 2.4.7 / 8.2',
            IReferenceNumber(self.subdossier).get_number())

    def test_use_formatter_configured_in_registry(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.formatter = 'grouped_by_three'

        self.assertEquals(
            'OG 247-8.2',
            IReferenceNumber(self.subdossier).get_number())


class TestDottedFormatter(FunctionalTestCase):

    def setUp(self):
        super(TestDottedFormatter, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter, name='dotted')

    def test_separate_repositories_with_a_dot(self):
        numbers = {'repository': [u'5', u'7', u'3', u'2'], }

        self.assertEquals(
            '5.7.3.2',
            self.formatter.repository_number(numbers))

    def test_separate_dossiers_and_subdossiers_with_a_dot(self):
        numbers = {'dossier': [u'4', u'6', u'2'], }

        self.assertEquals(
            '4.6.2',
            self.formatter.dossier_number(numbers))

    def test_repository_part_is_separated_with_space(self):
        numbers = {'site': ['OG', ],
                   'repository': [u'5', u'7', u'3', u'2']}

        self.assertEquals(
            'OG 5.7.3.2',
            self.formatter.complete_number(numbers))

    def test_dossier_part_is_separated_with_slash_and_spaces(self):
        numbers = {'site': ['OG', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2']}

        self.assertEquals(
            'OG 5.7.3.2 / 4.6.2',
            self.formatter.complete_number(numbers))


class TestGroupedbyThreeFormatter(FunctionalTestCase):

    def setUp(self):
        super(TestGroupedbyThreeFormatter, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter, name='grouped_by_three')

    def test_group_repositories_by_three_and_seperate_with_a_dot(self):
        numbers = {'repository': [u'5', u'7', u'3', u'2'], }

        self.assertEquals(
            '573.2', self.formatter.repository_number(numbers))

    def test_separate_dossiers_and_subdossiers_with_a_dot(self):
        numbers = {'dossier': [u'4', u'6', u'2'], }

        self.assertEquals(
            '4.6.2', self.formatter.dossier_number(numbers))

    def test_repository_part_is_separated_with_space(self):
        numbers = {'site': ['OG', ],
                   'repository': [u'5', u'7', u'3', u'2']}

        self.assertEquals(
            'OG 573.2', self.formatter.complete_number(numbers))

    def test_dossier_part_is_separated_with_hyphen(self):
        numbers = {'site': ['OG', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2']}

        self.assertEquals(
            'OG 573.2-4.6.2', self.formatter.complete_number(numbers))

    def test_document_part_is_separated_with_hyphen_and_spaces(self):
        numbers = {'site': ['OG', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2'],
                   'document': [u'27']}

        self.assertEquals(
            'OG 573.2-4.6.2-27', self.formatter.complete_number(numbers))


class TestDottedFormatSorter(TestDottedFormatter):
    def test_orders_first_level_refnums_correctly(self):
        expected = ['OG 1.9.9 / 9.9.9',
                    'OG 3.9.9 / 9.9.9',
                    'OG 11.9.9 / 9.9.9',]

        unordered = ['OG 3.9.9 / 9.9.9',
                     'OG 1.9.9 / 9.9.9',
                     'OG 11.9.9 / 9.9.9',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_second_level_refnums_correctly(self):
        expected = ['OG 9.1.9 / 9.9.9',
                    'OG 9.3.9 / 9.9.9',
                    'OG 9.11.9 / 9.9.9',]

        unordered = ['OG 9.3.9 / 9.9.9',
                     'OG 9.11.9 / 9.9.9',
                     'OG 9.1.9 / 9.9.9',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_main_dossiers_correctly(self):
        expected = ['OG 9.9.9.9 / 1.9',
                    'OG 9.9.9.9 / 3.9',
                    'OG 9.9.9.9 / 11.9',]

        unordered = ['OG 9.9.9.9 / 11.9',
                     'OG 9.9.9.9 / 3.9',
                     'OG 9.9.9.9 / 1.9',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)


    def test_orders_subdossiers_correctly(self):
        expected = ['OG 9.9.9.9 / 9.1',
                    'OG 9.9.9.9 / 9.3',
                    'OG 9.9.9.9 / 9.11',]

        unordered = ['OG 9.9.9.9 / 9.11',
                     'OG 9.9.9.9 / 9.3',
                     'OG 9.9.9.9 / 9.1',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)


    def test_orders_documents_correctly(self):
        expected = ['OG 9.9.9.9 / 9.9.9 / 1',
                    'OG 9.9.9.9 / 9.9.9 / 3',
                    'OG 9.9.9.9 / 9.9.9 / 11',]

        unordered = ['OG 9.9.9.9 / 9.9.9 / 11',
                     'OG 9.9.9.9 / 9.9.9 / 3',
                     'OG 9.9.9.9 / 9.9.9 / 1',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)


class TestGroupedbyThreeFormatSorter(TestGroupedbyThreeFormatter):

    def test_orders_first_level_refnums_correctly(self):
        expected = ['OG 01.0-9.9.9-99',
                    'OG 010.0-9.9.9-99',
                    'OG 011.0-9.9.9-99',
                    'OG 02.0-9.9.9-99',
                    'OG 020.0-9.9.9-99',
                    'OG 021.0-9.9.9-99',]

        unordered = ['OG 021.0-9.9.9-99',
                     'OG 010.0-9.9.9-99',
                     'OG 020.0-9.9.9-99',
                     'OG 011.0-9.9.9-99',
                     'OG 02.0-9.9.9-99',
                     'OG 01.0-9.9.9-99',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_second_level_refnums_correctly(self):
        expected = ['OG 021.1-9.9.9-99',
                    'OG 021.11-9.9.9-99',
                    'OG 021.111-9.9.9-99',]

        unordered = ['OG 021.11-9.9.9-99',
                     'OG 021.1-9.9.9-99',
                     'OG 021.111-9.9.9-99',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_main_dossiers_correctly(self):
        expected = ['OG 99.9-1.1-99',
                    'OG 99.9-3.1-99',
                    'OG 99.9-11.1-99',]

        unordered = ['OG 99.9-3.1-99',
                     'OG 99.9-1.1-99',
                     'OG 99.9-11.1-99',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_subdossiers_correctly(self):
        expected = ['OG 99.9-9.1-99',
                    'OG 99.9-9.3-99',
                    'OG 99.9-9.11-99',]

        unordered = ['OG 99.9-9.3-99',
                     'OG 99.9-9.1-99',
                     'OG 99.9-9.11-99',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_documents_correctly(self):
        expected = ['OG 99.9-9.9.9-1',
                    'OG 99.9-9.9.9-3',
                    'OG 99.9-9.9.9-11',]

        unordered = ['OG 99.9-9.9.9-3',
                     'OG 99.9-9.9.9-1',
                     'OG 99.9-9.9.9-11',]

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)
