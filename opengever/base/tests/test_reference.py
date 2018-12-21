from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import queryAdapter


class TestLocalReferenceNumber(IntegrationTestCase):

    def test_plone_site_returns_admin_units_abbreviation(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'Client1', IReferenceNumber(self.portal).get_local_number())

    def test_repository_root_returns_empty_string(self):
        self.login(self.regular_user)

        self.assertEquals(
            '', IReferenceNumber(self.repository_root).get_local_number())

    def test_repositoryfolder_returns_reference_prefix_of_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'2', IReferenceNumber(self.empty_repofolder).get_local_number())

    def test_dossier_returns_reference_prefix_of_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'1', IReferenceNumber(self.dossier).get_local_number())


class TestReferenceNumberAdapter(IntegrationTestCase):

    def test_returns_full_number_for_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            {'site': [u'Client1', ],
             'repositoryroot': [''],
             'repository': [u'1', u'1'],
             'dossier': [u'1', u'1']},
            IReferenceNumber(self.subdossier).get_parent_numbers())

    def test_use_dotted_as_default_formatter(self):
        self.login(self.regular_user)

        self.assertEquals(
            'Client1 1.1 / 1.1',
            IReferenceNumber(self.subdossier).get_number())

    def test_use_grouped_by_three_formatter(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter', value='grouped_by_three',
            interface=IReferenceNumberSettings)

        self.assertEquals(
            'Client1 11-1.1',
            IReferenceNumber(self.subdossier).get_number())

    def test_use_no_client_id_dotted_formatter(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter', value='no_client_id_dotted',
            interface=IReferenceNumberSettings)

        self.assertEquals(
            '1.1 / 1.1',
            IReferenceNumber(self.subdossier).get_number())

    def test_use_no_client_id_grouped_by_three_formatter(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter', value='no_client_id_grouped_by_three',
            interface=IReferenceNumberSettings)

        self.assertEquals(
            '11-1.1',
            IReferenceNumber(self.subdossier).get_number())


class TestDottedFormatterBase(IntegrationTestCase):

    def setUp(self):
        super(TestDottedFormatterBase, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter, name='dotted')


class TestDottedFormatter(TestDottedFormatterBase):

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
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2']}

        self.assertEquals(
            'Client1 5.7.3.2',
            self.formatter.complete_number(numbers))

    def test_dossier_part_is_separated_with_slash_and_spaces(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2']}

        self.assertEquals(
            'Client1 5.7.3.2 / 4.6.2',
            self.formatter.complete_number(numbers))

    def test_list_to_string(self):
        self.assertEquals(
            'Client1 1.4.5',
            self.formatter.list_to_string([[1, 4, 5]]))

        self.assertEquals(
            'Client1 1.4.5 / 452.4',
            self.formatter.list_to_string([[1, 4, 5], [452, 4]]))

        self.assertEquals(
            'Client1 1.4.5 / 452.4 / 135',
            self.formatter.list_to_string([[1, 4, 5], [452, 4], [135]]))


class TestGroupedbyThreeFormatterBase(IntegrationTestCase):

    def setUp(self):
        super(TestGroupedbyThreeFormatterBase, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter, name='grouped_by_three')


class TestGroupedbyThreeFormatter(TestGroupedbyThreeFormatterBase):

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

    def test_list_to_string(self):
        self.assertEquals(
            'Client1 145.72',
            self.formatter.list_to_string([[1, 4, 5, 7, 2]]))

        self.assertEquals(
            'Client1 145.72-452.4',
            self.formatter.list_to_string([[1, 4, 5, 7, 2], [452, 4]]))

        self.assertEquals(
            'Client1 145.72-452.4-135',
            self.formatter.list_to_string([[1, 4, 5, 7, 2], [452, 4], [135]]))


class TestNoClientIDGroupedbyThreeFormatterBase(IntegrationTestCase):

    def setUp(self):
        super(TestNoClientIDGroupedbyThreeFormatterBase, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter,
            name='no_client_id_grouped_by_three')


class TestNoClientIDGroupedbyThreeFormatter(TestNoClientIDGroupedbyThreeFormatterBase):

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
            '573.2', self.formatter.complete_number(numbers))

    def test_dossier_part_is_separated_with_hyphen(self):
        numbers = {'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2']}

        self.assertEquals(
            '573.2-4.6.2', self.formatter.complete_number(numbers))

    def test_document_part_is_separated_with_hyphen_and_spaces(self):
        numbers = {'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2'],
                   'document': [u'27']}

        self.assertEquals(
            '573.2-4.6.2-27', self.formatter.complete_number(numbers))

    def test_list_to_string(self):
        self.assertEquals(
            '145.72',
            self.formatter.list_to_string([[1, 4, 5, 7, 2]]))

        self.assertEquals(
            '145.72-452.4',
            self.formatter.list_to_string([[1, 4, 5, 7, 2], [452, 4]]))

        self.assertEquals(
            '145.72-452.4-135',
            self.formatter.list_to_string([[1, 4, 5, 7, 2], [452, 4], [135]]))


class TestDottedFormatSorter(TestDottedFormatterBase):

    def test_orders_standalone_repofolders_correctly(self):
        expected = ['OG 1.9.9',
                    'OG 3.9.9',
                    'OG 11.9.9']

        unordered = ['OG 3.9.9',
                     'OG 1.9.9',
                     'OG 11.9.9']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_first_level_refnums_correctly(self):
        expected = ['OG 1.9.9 / 9.9.9',
                    'OG 3.9.9 / 9.9.9',
                    'OG 11.9.9 / 9.9.9']

        unordered = ['OG 3.9.9 / 9.9.9',
                     'OG 1.9.9 / 9.9.9',
                     'OG 11.9.9 / 9.9.9']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_second_level_refnums_correctly(self):
        expected = ['OG 9.1.9 / 9.9.9',
                    'OG 9.3.9 / 9.9.9',
                    'OG 9.11.9 / 9.9.9']

        unordered = ['OG 9.3.9 / 9.9.9',
                     'OG 9.11.9 / 9.9.9',
                     'OG 9.1.9 / 9.9.9']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_main_dossiers_correctly(self):
        expected = ['OG 9.9.9.9 / 1.9',
                    'OG 9.9.9.9 / 3.9',
                    'OG 9.9.9.9 / 11.9']

        unordered = ['OG 9.9.9.9 / 11.9',
                     'OG 9.9.9.9 / 3.9',
                     'OG 9.9.9.9 / 1.9']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_subdossiers_correctly(self):
        expected = ['OG 9.9.9.9 / 9.1',
                    'OG 9.9.9.9 / 9.3',
                    'OG 9.9.9.9 / 9.11']

        unordered = ['OG 9.9.9.9 / 9.11',
                     'OG 9.9.9.9 / 9.3',
                     'OG 9.9.9.9 / 9.1']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_documents_correctly(self):
        expected = ['OG 9.9.9.9 / 9.9.9 / 1',
                    'OG 9.9.9.9 / 9.9.9 / 3',
                    'OG 9.9.9.9 / 9.9.9 / 11']

        unordered = ['OG 9.9.9.9 / 9.9.9 / 11',
                     'OG 9.9.9.9 / 9.9.9 / 3',
                     'OG 9.9.9.9 / 9.9.9 / 1']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)


class TestGroupedbyThreeFormatSorter(TestGroupedbyThreeFormatterBase):

    def test_orders_standalone_repofolders_correctly(self):
        # Zero-padded
        expected_1 = [
            'OG 01.0',
            'OG 010.0',
            'OG 011.0',
            'OG 02.0',
            'OG 020.0',
            'OG 021.0']

        unordered_1 = [
            'OG 021.0',
            'OG 010.0',
            'OG 020.0',
            'OG 011.0',
            'OG 02.0',
            'OG 01.0']

        # Unpadded
        expected_2 = [
            'OG 0',
            'OG 00',
            'OG 000',
            'OG 001',
            'OG 01',
            'OG 011',
            'OG 1']

        unordered_2 = [
            'OG 1',
            'OG 000',
            'OG 0',
            'OG 00',
            'OG 011',
            'OG 01',
            'OG 001']

        actual_1 = sorted(unordered_1, key=self.formatter.sorter)
        self.assertEquals(expected_1, actual_1)

        actual_2 = sorted(unordered_2, key=self.formatter.sorter)
        self.assertEquals(expected_2, actual_2)

    def test_orders_first_level_refnums_correctly(self):
        expected = ['OG 01.0-9.9.9-99',
                    'OG 010.0-9.9.9-99',
                    'OG 011.0-9.9.9-99',
                    'OG 02.0-9.9.9-99',
                    'OG 020.0-9.9.9-99',
                    'OG 021.0-9.9.9-99']

        unordered = ['OG 021.0-9.9.9-99',
                     'OG 010.0-9.9.9-99',
                     'OG 020.0-9.9.9-99',
                     'OG 011.0-9.9.9-99',
                     'OG 02.0-9.9.9-99',
                     'OG 01.0-9.9.9-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_second_level_refnums_correctly(self):
        expected = ['OG 021.1-9.9.9-99',
                    'OG 021.11-9.9.9-99',
                    'OG 021.111-9.9.9-99']

        unordered = ['OG 021.11-9.9.9-99',
                     'OG 021.1-9.9.9-99',
                     'OG 021.111-9.9.9-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_main_dossiers_correctly(self):
        expected = ['OG 99.9-1.1-99',
                    'OG 99.9-3.1-99',
                    'OG 99.9-11.1-99']

        unordered = ['OG 99.9-3.1-99',
                     'OG 99.9-1.1-99',
                     'OG 99.9-11.1-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_subdossiers_correctly(self):
        expected = ['OG 99.9-9.1-99',
                    'OG 99.9-9.3-99',
                    'OG 99.9-9.11-99']

        unordered = ['OG 99.9-9.3-99',
                     'OG 99.9-9.1-99',
                     'OG 99.9-9.11-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_documents_correctly(self):
        expected = ['OG 99.9-9.9.9-1',
                    'OG 99.9-9.9.9-3',
                    'OG 99.9-9.9.9-11']

        unordered = ['OG 99.9-9.9.9-3',
                     'OG 99.9-9.9.9-1',
                     'OG 99.9-9.9.9-11']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)


class TestNoClientIDGBTSorter(TestNoClientIDGroupedbyThreeFormatterBase):

    def test_orders_standalone_repofolders_correctly(self):
        # Zero-padded
        expected_1 = [
            '01.0',
            '010.0',
            '011.0',
            '02.0',
            '020.0',
            '021.0']

        unordered_1 = [
            '021.0',
            '010.0',
            '020.0',
            '011.0',
            '02.0',
            '01.0']

        # Unpadded
        expected_2 = [
            'OG 0',
            'OG 00',
            'OG 000',
            'OG 001',
            'OG 01',
            'OG 011',
            'OG 1']

        unordered_2 = [
            'OG 1',
            'OG 000',
            'OG 0',
            'OG 00',
            'OG 011',
            'OG 01',
            'OG 001']

        actual_1 = sorted(unordered_1, key=self.formatter.sorter)
        self.assertEquals(expected_1, actual_1)

        actual_2 = sorted(unordered_2, key=self.formatter.sorter)
        self.assertEquals(expected_2, actual_2)

    def test_orders_first_level_refnums_correctly(self):
        expected = ['01.0-9.9.9-99',
                    '010.0-9.9.9-99',
                    '011.0-9.9.9-99',
                    '02.0-9.9.9-99',
                    '020.0-9.9.9-99',
                    '021.0-9.9.9-99']

        unordered = ['021.0-9.9.9-99',
                     '010.0-9.9.9-99',
                     '020.0-9.9.9-99',
                     '011.0-9.9.9-99',
                     '02.0-9.9.9-99',
                     '01.0-9.9.9-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_second_level_refnums_correctly(self):
        expected = ['021.1-9.9.9-99',
                    '021.11-9.9.9-99',
                    '021.111-9.9.9-99']

        unordered = ['021.11-9.9.9-99',
                     '021.1-9.9.9-99',
                     '021.111-9.9.9-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_main_dossiers_correctly(self):
        expected = ['99.9-1.1-99',
                    '99.9-3.1-99',
                    '99.9-11.1-99']

        unordered = ['99.9-3.1-99',
                     '99.9-1.1-99',
                     '99.9-11.1-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_subdossiers_correctly(self):
        expected = ['99.9-9.1-99',
                    '99.9-9.3-99',
                    '99.9-9.11-99']

        unordered = ['99.9-9.3-99',
                     '99.9-9.1-99',
                     '99.9-9.11-99']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)

    def test_orders_documents_correctly(self):
        expected = ['99.9-9.9.9-1',
                    '99.9-9.9.9-3',
                    '99.9-9.9.9-11']

        unordered = ['99.9-9.9.9-3',
                     '99.9-9.9.9-1',
                     '99.9-9.9.9-11']

        actual = sorted(unordered, key=self.formatter.sorter)
        self.assertEquals(expected, actual)
