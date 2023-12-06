from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.contact.tests import create_contacts
from opengever.testing import IntegrationTestCase
from plone import api
from unittest import skip
from zope.component import queryAdapter


class TestLocalReferenceNumber(IntegrationTestCase):

    def test_plone_site_returns_admin_units_abbreviation(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'Client1', IReferenceNumber(self.portal).get_local_number())

    def test_repository_root_returns_empty_string(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'', IReferenceNumber(self.repository_root).get_local_number())

    def test_repository_root_returns_reference_number_addendum(self):
        self.login(self.regular_user)
        self.repository_root.reference_number_addendum = u'NO'

        self.assertEquals(
            u'NO', IReferenceNumber(self.repository_root).get_local_number())

    def test_repositoryfolder_returns_reference_prefix_of_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'2', IReferenceNumber(self.empty_repofolder).get_local_number())

    def test_dossier_returns_reference_prefix_of_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'1', IReferenceNumber(self.dossier).get_local_number())

    def test_document_returns_sequence_number_of_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'14', IReferenceNumber(self.document).get_local_number())

    def test_task_returns_empty_string(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'', IReferenceNumber(self.task).get_local_number())

    def test_committee_container_returns_empty_string(self):
        self.login(self.meeting_user)

        self.assertEquals(
            u'', IReferenceNumber(self.committee_container).get_local_number())

    def test_committee_returns_empty_string(self):
        self.login(self.meeting_user)

        self.assertEquals(
            u'', IReferenceNumber(self.committee).get_local_number())

    def test_proposal_returns_empty_string(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'', IReferenceNumber(self.proposal).get_local_number())

    def test_inbox_container_returns_empty_string(self):
        self.login(self.secretariat_user)

        self.assertEquals(
            u'', IReferenceNumber(self.inbox_container).get_local_number())

    def test_inbox_returns_inbox_id(self):
        self.login(self.secretariat_user)

        self.assertEquals(
            u'eingangskorb_fa', IReferenceNumber(self.inbox).get_local_number())

    def test_contactfolder_returns_empty_string(self):
        create_contacts(self)
        self.login(self.secretariat_user)

        self.assertEquals(
            u'', IReferenceNumber(self.contactfolder).get_local_number())

    def test_contact_returns_empty_string(self):
        create_contacts(self)
        self.login(self.regular_user)

        self.assertEquals(
            u'', IReferenceNumber(self.franz_meier).get_local_number())

    def test_private_root_returns_location_prefix(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'P', IReferenceNumber(self.private_root).get_local_number())

    @skip('Private folder reference prefix should be based on username')
    def test_private_folder_returns_urlified_username(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'kathi-barfuss',
            IReferenceNumber(self.private_folder).get_local_number())

    def test_private_dossier_returns_reference_prefix_of_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'1',
            IReferenceNumber(self.private_dossier).get_local_number())

    def test_template_folder_returns_id(self):
        self.login(self.regular_user)

        self.assertEquals(
            'vorlagen',
            IReferenceNumber(self.templates).get_local_number())


class TestReferenceNumberAdapter(IntegrationTestCase):

    def test_returns_full_number_for_the_context(self):
        self.login(self.regular_user)

        self.assertEquals(
            {'site': [u'Client1', ],
             'repositoryroot': [''],
             'repository': [u'1', u'1'],
             'dossier': [u'1', u'1']},
            IReferenceNumber(self.subdossier).get_numbers())

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

    def test_dotted_sortable_reference_number(self):
        self.login(self.regular_user)

        self.assertEquals(
            'client00000001 00000001.00000001 / 00000001.00000001.00000001 / 00000023',
            IReferenceNumber(self.subsubdocument).get_sortable_number())

    def test_grouped_by_three_sortable_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter', value='grouped_by_three',
            interface=IReferenceNumberSettings)

        self.assertEquals(
            'client00000001 0000000100000001-00000001.00000001.00000001-00000023',
            IReferenceNumber(self.subsubdocument).get_sortable_number())

    def test_no_client_id_dotted_sortable_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter', value='no_client_id_dotted',
            interface=IReferenceNumberSettings)

        self.assertEquals(
            '00000001.00000001 / 00000001.00000001.00000001 / 00000023',
            IReferenceNumber(self.subsubdocument).get_sortable_number())

    def test_no_client_id_grouped_by_three_sortable_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter', value='no_client_id_grouped_by_three',
            interface=IReferenceNumberSettings)

        self.assertEquals(
            '0000000100000001-00000001.00000001.00000001-00000023',
            IReferenceNumber(self.subsubdocument).get_sortable_number())

    def test_reference_number_for_plone_site(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1',
                          IReferenceNumber(self.portal).get_number())

    def test_reference_number_for_repository_root(self):
        self.login(self.regular_user)

        self.assertEquals("Client1",
                          IReferenceNumber(self.repository_root).get_number())

    def test_reference_number_for_repositoryfolder(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1 1.1',
                          IReferenceNumber(self.leaf_repofolder).get_number())

    def test_reference_number_for_dossier(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1 1.1 / 1.1',
                          IReferenceNumber(self.subdossier).get_number())

    def test_reference_number_for_document(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1 1.1 / 1.1.1 / 23',
                          IReferenceNumber(self.subsubdocument).get_number())

    def test_reference_number_for_task(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1 1.1 / 1',
                          IReferenceNumber(self.subtask).get_number())

    def test_reference_number_for_committee_container(self):
        self.login(self.meeting_user)

        self.assertEquals(u'Client1',
                          IReferenceNumber(self.committee_container).get_number())

    def test_reference_number_for_committee(self):
        self.login(self.meeting_user)

        self.assertEquals(u'Client1',
                          IReferenceNumber(self.committee).get_number())

    def test_reference_number_for_proposal(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1 1.1 / 1',
                          IReferenceNumber(self.proposal).get_number())

    def test_reference_number_for_proposal_document(self):
        self.login(self.regular_user)

        self.assertEquals(u'Client1 1.1 / 1 / 18',
                          IReferenceNumber(self.proposaldocument).get_number())

    def test_reference_number_for_inbox_container(self):
        self.login(self.secretariat_user)

        self.assertEquals(u'Client1',
                          IReferenceNumber(self.inbox_container).get_number())

    def test_reference_number_for_inbox(self):
        self.login(self.secretariat_user)

        self.assertEquals(u'eingangskorb_fa Client1',
                          IReferenceNumber(self.inbox).get_number())

    def test_reference_number_for_contactfolder(self):
        create_contacts(self)
        self.login(self.secretariat_user)

        self.assertEquals(u'Client1',
                          IReferenceNumber(self.contactfolder).get_number())

    def test_reference_number_for_contact(self):
        create_contacts(self)
        self.login(self.regular_user)

        self.assertEquals(u'Client1',
                          IReferenceNumber(self.franz_meier).get_number())

    def test_reference_number_for_private_root(self):
        self.login(self.regular_user)

        self.assertEquals(u'P Client1',
                          IReferenceNumber(self.private_root).get_number())

    @skip('Private folder reference prefix should be based on username')
    def test_reference_number_for_private_folder(self):
        self.login(self.regular_user)

        self.assertEquals(u'P Client1 kathi-barfuss',
                          IReferenceNumber(self.private_folder).get_number())

    @skip('Private folder reference prefix should be based on username')
    def test_reference_number_for_private_dossier(self):
        self.login(self.regular_user)

        self.assertEquals(u'P Client1 kathi-barfuss / 1',
                          IReferenceNumber(self.private_dossier).get_number())

    def test_reference_number_for_template_folder(self):
        self.login(self.regular_user)

        self.assertEquals(u'vorlagen Client1',
                          IReferenceNumber(self.templates).get_number())

    def test_reference_number_for_document_template(self):
        self.login(self.regular_user)

        self.assertEquals(u'vorlagen Client1 / 3',
                          IReferenceNumber(self.empty_template).get_number())

    def test_reference_number_for_tasktemplate(self):
        self.login(self.regular_user)

        self.assertEquals(u'vorlagen Client1',
                          IReferenceNumber(self.tasktemplate).get_number())

    def test_reference_number_for_dossiertemplate(self):
        self.login(self.regular_user)

        self.assertEquals(u'vorlagen Client1',
                          IReferenceNumber(self.subdossiertemplate).get_number())

    def test_reference_number_contains_addendum(self):
        self.login(self.regular_user)
        self.repository_root.reference_number_addendum = u'NO'

        self.assertEquals(u'Client1 NO 1.1 / 1.1',
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


class TestSortableReferenceNumberForDottedFormatter(TestDottedFormatterBase):

    def setUp(self):
        super(TestSortableReferenceNumberForDottedFormatter, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter, name='dotted')

    def test_pad_and_separate_repositories_with_a_dot(self):
        numbers = {'repository': [u'5', u'7', u'3', u'2'], }

        self.assertEquals(
            '00000005.00000007.00000003.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_repository_alpanumeric_parts(self):
        numbers = {'repository': [u'5 foo', u'bar7', u'foo3-4bar'], }

        self.assertEquals(
            '00000005 foo.bar00000007.foo00000003-00000004bar',
            self.formatter.complete_sortable_number(numbers))

    def test_pad_and_separate_dossiers_and_subdossiers_with_a_dot(self):
        numbers = {'dossier': [u'4', u'6', u'2'], }

        self.assertEquals(
            ' / 00000004.00000006.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_repository_part_is_separated_with_space(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2']}

        self.assertEquals(
            'client00000001 00000005.00000007.00000003.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_dossier_part_is_separated_with_slash_and_spaces(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2']}

        self.assertEquals(
            'client00000001 00000005.00000007.00000003.00000002 / '
            '00000004.00000006.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_document_part_is_padded_and_separated_with_slash_and_space(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2'],
                   'document': ['213']}

        self.assertEquals(
            'client00000001 00000005.00000007.00000003.00000002 / '
            '00000004.00000006.00000002 / 00000213',
            self.formatter.complete_sortable_number(numbers))

    def test_sorting_clients_on_sortable_reference_number(self):
        numbers_list = [
            {'site': ['Client1'], 'repository': ['10']},
            {'site': ['Client10'], 'repository': ['1']},
            {'site': ['Client2'], 'repository': ['1']},
            {'site': ['Foo'], 'repository': ['6']},
            {'site': ['bar'], 'repository': ['1', '1']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['bar 00000001.00000001',
             'client00000001 00000010',
             'client00000002 00000001',
             'client00000010 00000001',
             'foo 00000006'],
            sorted(sortable_numbers))

    def test_sorting_respositories_on_sortable_reference_number(self):
        numbers_list = [
            {'site': ['fd'], 'repository': ['10']},
            {'site': ['fd'], 'repository': ['1']},
            {'site': ['fd'], 'repository': ['6']},
            {'site': ['fd'], 'repository': ['1', '1']},
            {'site': ['fd'], 'repository': ['12']},
            {'site': ['fd'], 'repository': ['5']},
            {'site': ['fd'], 'repository': ['1', '10', '2']},
            {'site': ['fd'], 'repository': ['1', '10']},
            {'site': ['fd'], 'repository': ['1', '8', '1']},
            {'site': ['fd'], 'repository': ['10', '0']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['fd 00000001',
             'fd 00000001.00000001',
             'fd 00000001.00000008.00000001',
             'fd 00000001.00000010',
             'fd 00000001.00000010.00000002',
             'fd 00000005',
             'fd 00000006',
             'fd 00000010',
             'fd 00000010.00000000',
             'fd 00000012'],
            sorted(sortable_numbers))

    def test_sorting_dossiers_on_sortable_reference_number(self):
        numbers_list = [
            {'site': ['fd'], 'repository': ['10'], 'dossier': ['6']},
            {'site': ['fd'], 'repository': ['1'], 'dossier': ['0']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['1']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['10']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['3']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['1', '2']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['1', '10']},
            {'site': ['fd'], 'repository': ['1', '0'], 'dossier': ['8']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['fd 00000001 / 00000000',
             'fd 00000001.00000000 / 00000008',
             'fd 00000001.00000001 / 00000001',
             'fd 00000001.00000001 / 00000001.00000002',
             'fd 00000001.00000001 / 00000001.00000010',
             'fd 00000001.00000001 / 00000003',
             'fd 00000001.00000001 / 00000010',
             'fd 00000010 / 00000006'],
            sorted(sortable_numbers))

    def test_dossier_are_sorted_before_repositories(self):
        numbers_list = [
            {'repository': ['1', '1']},
            {'repository': ['1', '1'], 'dossier': ['2']},
            {'repository': ['1', '1', '1']},
            {'repository': ['1', '1', '1'], 'dossier': ['2']},
            {'repository': ['1', '1', '1', '1']},
            {'repository': ['1', '1', '1', '1'], 'dossier': ['2']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['00000001.00000001',
             '00000001.00000001 / 00000002',
             '00000001.00000001.00000001',
             '00000001.00000001.00000001 / 00000002',
             '00000001.00000001.00000001.00000001',
             '00000001.00000001.00000001.00000001 / 00000002'],
            sorted(sortable_numbers))

    def test_documents_are_sorted_before_subdossiers(self):
        numbers_list = [
            {'repository': ['1'], 'dossier': ['1']},
            {'repository': ['1'], 'dossier': ['1'], 'document': ['2']},
            {'repository': ['1'], 'dossier': ['1', '1']},
            {'repository': ['1'], 'dossier': ['1', '1'], 'document': ['2']},
            {'repository': ['1'], 'dossier': ['1', '1', '1']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['00000001 / 00000001',
             '00000001 / 00000001 / 00000002',
             '00000001 / 00000001.00000001',
             '00000001 / 00000001.00000001 / 00000002',
             '00000001 / 00000001.00000001.00000001'],
            sorted(sortable_numbers))


class TestSortableReferenceNumberForGroupedByThreeFormatter(TestDottedFormatterBase):

    def setUp(self):
        super(TestSortableReferenceNumberForGroupedByThreeFormatter, self).setUp()

        self.formatter = queryAdapter(
            self.portal, IReferenceNumberFormatter, name='grouped_by_three')

    def test_pad_and_separate_repository_groups_with_a_dot(self):
        numbers = {'repository': [u'5', u'7', u'3', u'2'], }

        self.assertEquals(
            '000000050000000700000003.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_repository_alpanumeric_parts(self):
        numbers = {'repository': [u'5 foo', u'bar7', u'foo3-4bar'], }

        self.assertEquals(
            '00000005 foobar00000007foo00000003-00000004bar',
            self.formatter.complete_sortable_number(numbers))

    def test_pad_and_separate_dossier_groups_with_a_dot(self):
        numbers = {'dossier': [u'4', u'6', u'2', '7', '3'], }

        self.assertEquals(
            '-00000004.00000006.00000002.00000007.00000003',
            self.formatter.complete_sortable_number(numbers))

    def test_repository_part_is_separated_with_space(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2']}

        self.assertEquals(
            'client00000001 000000050000000700000003.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_dossier_part_is_separated_with_dash(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2']}

        self.assertEquals(
            'client00000001 000000050000000700000003.00000002-'
            '00000004.00000006.00000002',
            self.formatter.complete_sortable_number(numbers))

    def test_document_part_is_padded_and_separated_with_dash(self):
        numbers = {'site': ['Client1', ],
                   'repository': [u'5', u'7', u'3', u'2'],
                   'dossier': [u'4', u'6', u'2'],
                   'document': ['213']}

        self.assertEquals(
            'client00000001 000000050000000700000003.00000002-'
            '00000004.00000006.00000002-00000213',
            self.formatter.complete_sortable_number(numbers))

    def test_sorting_clients_on_sortable_reference_number(self):
        numbers_list = [
            {'site': ['Client1'], 'repository': ['7']},
            {'site': ['Client10'], 'repository': ['1']},
            {'site': ['Client2'], 'repository': ['1']},
            {'site': ['Foo'], 'repository': ['6']},
            {'site': ['bar'], 'repository': ['1', '1']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['bar 0000000100000001',
             'client00000001 00000007',
             'client00000002 00000001',
             'client00000010 00000001',
             'foo 00000006'],
            sorted(sortable_numbers))

    def test_sorting_respositories_on_sortable_reference_number(self):
        numbers_list = [
            {'site': ['fd'], 'repository': ['10']},
            {'site': ['fd'], 'repository': ['1']},
            {'site': ['fd'], 'repository': ['6']},
            {'site': ['fd'], 'repository': ['1', '1']},
            {'site': ['fd'], 'repository': ['12']},
            {'site': ['fd'], 'repository': ['5']},
            {'site': ['fd'], 'repository': ['1', '10', '2']},
            {'site': ['fd'], 'repository': ['1', '10']},
            {'site': ['fd'], 'repository': ['1', '8', '1']},
            {'site': ['fd'], 'repository': ['10', '0']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['fd 00000001',
             'fd 0000000100000001',
             'fd 000000010000000800000001',
             'fd 0000000100000010',
             'fd 000000010000001000000002',
             'fd 00000005',
             'fd 00000006',
             'fd 00000010',
             'fd 0000001000000000',
             'fd 00000012'],
            sorted(sortable_numbers))

    def test_sorting_dossiers_on_sortable_reference_number(self):
        numbers_list = [
            {'site': ['fd'], 'repository': ['2'], 'dossier': ['6']},
            {'site': ['fd'], 'repository': ['1'], 'dossier': ['0']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['1']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['10']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['3']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['1', '2']},
            {'site': ['fd'], 'repository': ['1', '1'], 'dossier': ['1', '10']},
            {'site': ['fd'], 'repository': ['1', '0'], 'dossier': ['8']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['fd 00000001-00000000',
             'fd 0000000100000000-00000008',
             'fd 0000000100000001-00000001',
             'fd 0000000100000001-00000001.00000002',
             'fd 0000000100000001-00000001.00000010',
             'fd 0000000100000001-00000003',
             'fd 0000000100000001-00000010',
             'fd 00000002-00000006'],
            sorted(sortable_numbers))

    def test_dossier_are_sorted_before_repositories(self):
        numbers_list = [
            {'repository': ['1', '1']},
            {'repository': ['1', '1'], 'dossier': ['2']},
            {'repository': ['1', '1', '1']},
            {'repository': ['1', '1', '1'], 'dossier': ['2']},
            {'repository': ['1', '1', '1', '1']},
            {'repository': ['1', '1', '1', '1'], 'dossier': ['2']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['0000000100000001',
             '0000000100000001-00000002',
             '000000010000000100000001',
             '000000010000000100000001-00000002',
             '000000010000000100000001.00000001',
             '000000010000000100000001.00000001-00000002'],
            sorted(sortable_numbers))

    def test_documents_are_sorted_before_subdossiers(self):
        numbers_list = [
            {'repository': ['1'], 'dossier': ['1']},
            {'repository': ['1'], 'dossier': ['1'], 'document': ['2']},
            {'repository': ['1'], 'dossier': ['1', '1']},
            {'repository': ['1'], 'dossier': ['1', '1'], 'document': ['2']},
            {'repository': ['1'], 'dossier': ['1', '1', '1']}]

        sortable_numbers = [self.formatter.complete_sortable_number(numbers)
                            for numbers in numbers_list]

        self.assertEqual(
            ['00000001-00000001',
             '00000001-00000001-00000002',
             '00000001-00000001.00000001',
             '00000001-00000001.00000001-00000002',
             '00000001-00000001.00000001.00000001'],
            sorted(sortable_numbers))
