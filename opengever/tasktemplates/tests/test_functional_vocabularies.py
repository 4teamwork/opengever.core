# -*- coding: utf-8 -*-
from mocker import ANY
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.tasktemplates.vocabularies import interactive_users
from opengever.tasktemplates.vocabularies import \
    IssuerVocabularyFactory, ResponsibleClientVocabularyFactory,\
    ResponsibleVocabularyFactory
from plone.mocktestcase import MockTestCase


class TestFunctionalVocabularies(MockTestCase):
    """ Functional tests
    """

    def test_vocabulary_interactive_users(self):
        """ Test for interactive_users voca
        """
        # Context
        mock_context = self.mocker.mock()

        # Interactive users
        users = ['Responsible',
                 'Current user']

        self.replay()

        # Get the generator-object
        generator = interactive_users(mock_context)

        self.check_generator(generator, users)

    def test_IssuerVocabularyFactory(self):
        """ Test for IssuerVoca
        """
        # Context
        mock_context = self.mocker.mock()

        # Register Contact Information Utility
        self.register_contact_info_utility()

        # Register Sync Stamp Utility
        self.register_sync_stamp_utility()

        # Expected users
        users = ['Responsible',
                'Current user',
                'Contactinfo',
                'Client 1']

        # Patching context var from IssuerVocabFactory-Object
        VocabFactory = self.mocker.patch(
            IssuerVocabularyFactory())
        self.expect(VocabFactory.context).result(mock_context).count(0, None)

        self.replay()

        generator = VocabFactory.key_value_provider()

        self.check_generator(generator, users)

    def test_ResponsibleClientVocabularyFactory(self):
        """ Test for ResponsibleClientVoca
        """

        # Context
        mock_context = self.mocker.mock()

        # Register Contact Information Utility
        self.register_contact_info_utility()

        # Expected entries
        clients = ['Interactive users',
                   'Client 1']

        # Patching context var from ResponsibleClientVocabularyFactory-Object
        VocabFactory = self.mocker.patch(
            ResponsibleClientVocabularyFactory())
        self.expect(VocabFactory.context).result(mock_context).count(0, None)

        self.replay()

        generator = VocabFactory.key_value_provider()

        self.check_generator(generator, clients)

    def test_ResponsibleVocabularyFactory_1(self):
        """ Test with clients
        """

        # Expected entries
        users = ['Responsible',
                 'Current user',
                 'zopemaster']

        self.base_ResponsibleVocabularyFactory(users, 'interactive_users')

    def test_ResponsibleVocabularyFactory_2(self):
        """ Test with no clients
        """

        # Expected entries
        users = ['zopemaster',
                 'Contactinfo',
                 'Contactinfo']

        self.base_ResponsibleVocabularyFactory(users, 'bambi')

    def base_ResponsibleVocabularyFactory(self, users, get_client):
        """ Basetestmethod to test the responsiblevoca
        """

        # Context
        mock_context = self.mocker.mock()
        self.expect(
            mock_context.REQUEST.getURL()).result('/@@edit').count(0, None)
        self.expect(
            mock_context.responsible).result('zopemaster').count(0, None)

        # Register Contact Information Utility
        self.register_contact_info_utility()

        # Register Sync Stamp Utility
        self.register_sync_stamp_utility()

        # Patching context var from ResponsibleClientVocabularyFactory-Object
        VocabFactory = self.mocker.patch(
            ResponsibleVocabularyFactory())
        self.expect(VocabFactory.context).result(mock_context).count(0, None)
        self.expect(
            VocabFactory.get_client()).result(get_client).count(0, None)

        self.replay()

        generator = VocabFactory.key_value_provider()

        self.assertTrue(isinstance(generator, list))

        self.check_generator(generator, users)

    def check_generator(self, generator, expected):
        """ Checks the expected items in the generator
        """

        # To check the numbers of entries in voca
        check_gen = 0

        for item in generator:
            check_gen += 1
            self.assertTrue(item[1] in expected)

        # We must have two entries in voca
        self.assertTrue(check_gen == len(expected))

    def register_sync_stamp_utility(self):
        """ Register the IContactInformation utility
        """

        # Register Sync Stamp Utility
        mock_sync_stamp = self.mocker.mock()
        self.expect(
            mock_sync_stamp.get_sync_stamp()).result('').count(0, None)

        self.mock_utility(mock_sync_stamp, ISyncStamp, name=u"")

    def register_contact_info_utility(self):
        """ Register the IContactInformation utility
        """

        # Contact 1
        mock_contact1 = self.mocker.mock()
        self.expect(mock_contact1.active).result(True).count(0, None)
        self.expect(mock_contact1.userid).result('contact1').count(0, None)

        # Client 1
        mock_client1 = self.mocker.mock()
        self.expect(mock_client1.title).result('Client 1').count(0, None)
        self.expect(mock_client1.client_id).result('client1').count(0, None)

        # IContactInformationUtility
        mock_contact_info = self.mocker.mock()
        self.expect(
            mock_contact_info.list_users()).result(
                [mock_contact1]).count(0, None)
        self.expect(
            mock_contact_info.describe(ANY)).result(
                'Contactinfo').count(0, None)
        self.expect(
            mock_contact_info.get_clients()).result(
                [mock_client1]).count(0, None)
        self.expect(
            mock_contact_info.list_contacts()).result([]).count(0, None)
        self.expect(
            mock_contact_info.list_assigned_users(
                client_id=ANY)).result([mock_contact1]).count(0, None)
        self.expect(
            mock_contact_info.list_inactive_users()).result([]).count(0, None)

        self.mock_utility(mock_contact_info, IContactInformation, name=u"")
