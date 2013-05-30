from opengever.ogds.base import communication
from opengever.ogds.base.testing import create_contacts
from opengever.ogds.base.vocabulary import ContactsVocabulary
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.component import provideUtility
from zope.globalrequest import setRequest
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
import types


class TestContactVocabulary(FunctionalTestCase):

    def key_value_provider(self):
        yield ('first-entry', 'First Entry')
        yield ('second-entry', 'Second Entry')
        yield ('third-entry', 'Third Entry')
        yield ('fourth-entry', 'Fourth Entry')
        yield ('fifth-entry', 'Fifth Entry')

    def test_custom_search_handle_each_word_seperatly(self):
        voc = ContactsVocabulary.create_with_provider(self.key_value_provider)

        self.assertTerms(
            [('first-entry', 'First Entry'), ], voc.search('fir en'))
        self.assertTerms(
            [('first-entry', 'First Entry'), ], voc.search('en fir'))
        self.assertTerms(
            [('first-entry', 'First Entry'), ], voc.search('rst'))

    def test_custom_search_can_handle_multiple_results(self):
        voc = ContactsVocabulary.create_with_provider(self.key_value_provider)
        self.assertTerms(
            [('first-entry', 'First Entry'),
             ('second-entry', 'Second Entry'),
             ('third-entry', 'Third Entry'),
             ('fourth-entry', 'Fourth Entry'),
             ('fifth-entry', 'Fifth Entry'),],
            voc.search('entry'))

        self.assertTerms(
            [('first-entry', 'First Entry'), ('fifth-entry', 'Fifth Entry')],
            voc.search('fi en'))

    def test_custom_search_ignore_upper_case(self):
        voc = ContactsVocabulary.create_with_provider(self.key_value_provider)

        self.assertTerms(
            [('first-entry', 'First Entry')], voc.search('FIR EN'))

    def test_custom_search_is_not_fuzzy(self):
        voc = ContactsVocabulary.create_with_provider(self.key_value_provider)

        self.assertTerms([], voc.search('firt'))


class TestUsersVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestUsersVocabulary, self).setUp()
        self.voca_factory = getUtility(
            IVocabularyFactory, name='opengever.ogds.base.UsersVocabulary')

    def test_contains_all_active_users(self):
        create_ogds_user('hugo.boss', firstname='Hugo', lastname='Boss')
        create_ogds_user('peter.muster', firstname='Peter', lastname='Muster')
        create_ogds_user('hanspeter.linder', firstname='Hans-peter', lastname='Linder')

        self.assertTerms(
            [('hugo.boss', 'Boss Hugo (hugo.boss)'),
             ('peter.muster', 'Muster Peter (peter.muster)'),
             ('hanspeter.linder', 'Linder Hans-peter (hanspeter.linder)')],
            self.voca_factory(self.portal))

    def test_not_contains_inactive_users(self):
        create_ogds_user('robin.hood', firstname='Robin',
                         lastname='Hood', active=False)

        voc = self.voca_factory(self.portal)

        self.assertNotIn('robin.hood', [t.value for t in voc])

    def test_inactive_users_are_still_accessible_by_get_term(self):
        create_ogds_user('robin.hood', firstname='Robin',
                 lastname='Hood', active=False)

        voc = self.voca_factory(self.portal)

        self.assertEquals(
            u'Hood Robin (robin.hood)', voc.getTerm('robin.hood').title)


class TestUsersAndInboxesVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestUsersAndInboxesVocabulary, self).setUp()
        self.voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.UsersAndInboxesVocabulary')

        self.client1 = create_client(clientid="client1", title="Client 1")
        self.client2 = create_client(clientid="client2", title="Client 2")


    def test_contains_all_active_users_and_inboxes_assigned_to_the_given_client(self):
        create_ogds_user('hugo.boss', firstname='Hugo',
                         lastname='Boss', assigned_client=[self.client1, ])
        create_ogds_user('hanspeter.linder', firstname='Hanspeter',
                         lastname='Linder', assigned_client=[self.client1, self.client2])
        create_ogds_user('peter.muster', firstname='Peter',
                         lastname='Muster', assigned_client=[self.client2])

        self.portal.REQUEST.set('client', 'client2')

        self.assertTerms(
            [('hanspeter.linder', 'Linder Hanspeter (hanspeter.linder)'),
             ('peter.muster', 'Muster Peter (peter.muster)'),
             ('inbox:client2', 'Inbox: Client 2')],
            self.voca_factory(self.portal))

    def test_use_clientid_from_responsible_client_widget(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'client2')

        self.assertTerms([('inbox:client2', 'Inbox: Client 2')],
                         self.voca_factory(self.portal))

    def test_use_clientid_from_responsible_client_of_actual_context(self):
        self.portal.responsible_client = 'client2'

        self.assertTerms([('inbox:client2', 'Inbox: Client 2')],
                         self.voca_factory(self.portal))


class TestAllUsersAndInboxesVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestAllUsersAndInboxesVocabulary, self).setUp()
        self.voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.AllUsersAndInboxesVocabulary')

    def test_terms_are_marked_with_client_prefix(self):
        client1 = create_client(clientid="client1", title="Client 1")
        create_ogds_user('hugo.boss', firstname='Hugo',
                         lastname='Boss', assigned_client=[client1, ])
        set_current_client_id(self.portal)

        self.assertTerms(
            [('client1:hugo.boss', 'Client 1: Boss Hugo (hugo.boss)'),
             ('client1:inbox:client1', 'Inbox: Client 1')],
            self.voca_factory(self.portal))

    def test_has_multiple_terms_for_users_assigned_to_multiple_clients(self):
        client1 = create_client(clientid="client1", title="Client 1")
        client2 = create_client(clientid="client2", title="Client 2")
        create_ogds_user('hugo.boss', firstname='Hugo',
                         lastname='Boss', assigned_client=[client1, client2])
        set_current_client_id(self.portal)

        voc = self.voca_factory(self.portal)

        self.assertInTerms('client1:hugo.boss', voc)
        self.assertInTerms('client2:hugo.boss', voc)

    def test_inactive_clients_inboxes_are_not_included(self):
        client1 = create_client(clientid="client1", title="Client 1")
        client2 = create_client(
            clientid="client2", title="Client 2", enabled=False)
        set_current_client_id(self.portal)

        voc = self.voca_factory(self.portal)

        self.assertNotInTerms('client2:inbox', voc)
        self.assertInTerms('client1:inbox:client1', voc)


class TestAssignedUsersVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestAssignedUsersVocabulary, self).setUp()

        self.voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.AssignedUsersVocabulary')

    def test_contains_only_users_assigned_to_current_client(self):
        client1 = create_client(clientid="client1", title="Client 1")
        client2 = create_client(clientid="client2", title="Client 2")

        create_ogds_user('hugo.boss', firstname='Hugo',
                         lastname='Boss', assigned_client=[client1])
        create_ogds_user('peter.muster', firstname='Peter',
                         lastname='Muster', assigned_client=[client2])
        create_ogds_user('hanspeter.linder', firstname='Hans-peter',
                         lastname='Linder', assigned_client=[client1, client2])

        set_current_client_id(self.portal, clientid='client2')

        self.assertTerms(
            [(u'peter.muster', 'Muster Peter (peter.muster)'),
             (u'hanspeter.linder', 'Linder Hans-peter (hanspeter.linder)')],
            self.voca_factory(self.portal))

    def test_hidden_terms_contains_all_inactive_users(self):
        client1 = create_client(clientid="client1", title="Client 1")
        set_current_client_id(self.portal)

        create_ogds_user('robin.hood', assigned_client=[client1, ], active=False)
        create_ogds_user('hans.peter', active=False)

        voc = self.voca_factory(self.portal)

        self.assertEquals([u'robin.hood', u'hans.peter'], voc.hidden_terms)


class TestContactsAndUsersVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestContactsAndUsersVocabulary, self).setUp()
        set_current_client_id(self.portal)
        self.voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.ContactsAndUsersVocabulary')

    def test_contains_all_users_from_every_client(self):
        client1 = create_client(clientid="client1")
        client2 = create_client(clientid="client2")
        create_ogds_user('hugo.boss', assigned_client=[client1, ])
        create_ogds_user('robin.hood', assigned_client=[client2, ])

        voc = self.voca_factory(self.portal)

        self.assertInTerms('hugo.boss', voc)
        self.assertInTerms('robin.hood', voc)

    def test_contains_inboxes_from_every_active_client(self):
        create_client(clientid="client1")
        create_client(clientid="client2")
        create_client(clientid="client3", enabled=False)

        voc = self.voca_factory(self.portal)

        self.assertInTerms('inbox:client1', voc)
        self.assertInTerms('inbox:client2', voc)
        self.assertNotInTerms('inbox:client3', voc)

    def test_contains_all_local_contacts(self):
        create_client(clientid="client1")
        Builder('contact').having(
            firstname=u'Sandra', lastname=u'Kaufmann',
            email=u'sandra.kaufmann@test.ch').create()
        Builder('contact').having(
            firstname=u'Elisabeth', lastname=u'K\xe4ppeli',
            email= 'elisabeth.kaeppeli@test.ch').create()

        voc = self.voca_factory(self.portal)

        self.assertInTerms('contact:kaufmann-sandra', voc)
        self.assertInTerms('contact:kappeli-elisabeth', voc)


class TestEmailContactsAndUsersVocabularyFactory(FunctionalTestCase):

    def setUp(self):
        super(TestEmailContactsAndUsersVocabularyFactory, self).setUp()

        self.voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.EmailContactsAndUsersVocabulary')

    def test_contains_emails_for_all_users(self):
        create_ogds_user('hugo.boss', firstname=u'Hugo', lastname=u'Boss', email='hugo@boss.local')
        create_ogds_user('robin.hood', firstname=u'Robin', lastname=u'Hood', email='robin@hood.tld')

        self.assertTerms(
            [('hugo@boss.local:hugo.boss', 'Boss Hugo (hugo.boss, hugo@boss.local)'),
             (u'robin@hood.tld:robin.hood', 'Hood Robin (robin.hood, robin@hood.tld)')],
            self.voca_factory(self.portal))

    def test_contains_emails_for_all_contacts(self):
        Builder('contact').having(
            firstname=u'Sandra', lastname=u'Kaufmann',
            email=u'sandra.kaufmann@test.ch').create()
        Builder('contact').having(
            firstname=u'Elisabeth', lastname=u'K\xe4ppeli',
            email= 'elisabeth.kaeppeli@test.ch').create()

        self.assertTerms(
            [('sandra.kaufmann@test.ch:kaufmann-sandra',
              u'Kaufmann Sandra (sandra.kaufmann@test.ch)'),
             ('elisabeth.kaeppeli@test.ch:kappeli-elisabeth',
              u'K\xe4ppeli Elisabeth (elisabeth.kaeppeli@test.ch)')],
            self.voca_factory(self.portal))

    def test_has_an_entry_for_each_mail_address(self):
        create_ogds_user('hugo.boss', firstname=u'Hugo', lastname=u'Boss',
                         email='hugo@boss.local', email2='hugo@private.ch')

        self.assertTerms(
            [('hugo@boss.local:hugo.boss',
              'Boss Hugo (hugo.boss, hugo@boss.local)'),
             ('hugo@private.ch:hugo.boss',
              'Boss Hugo (hugo.boss, hugo@private.ch)')],
            self.voca_factory(self.portal))


class TestAssignedClientsVocabularies(FunctionalTestCase):

    def setUp(self):
        super(TestAssignedClientsVocabularies, self).setUp()

    def test_contains_all_clients_assigned_to_the_current_client(self):
        client1 = create_client(clientid='client1')
        set_current_client_id(self.portal, clientid=u'client1')
        create_client(clientid='client2')
        client3 = create_client(clientid='client3')
        create_ogds_user(TEST_USER_ID, assigned_client=[client1, client3])

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.AssignedClientsVocabulary')

        self.assertTerms(
            [('client1', 'Client1'),('client3', 'Client3')],
            voca_factory(self.portal))

    def test_other_assigned_vocabulary_does_not_include_the_current_client(self):
        client1 = create_client(clientid='client1')
        create_client(clientid='client2')
        client3 = create_client(clientid='client3')

        create_ogds_user(TEST_USER_ID, assigned_client=[client1, client3])
        set_current_client_id(self.portal)

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OtherAssignedClientsVocabulary')
        voc = voca_factory(self.portal)

        self.assertTerms([('client3', 'Client3')], voca_factory(self.portal))


class TestOGDSVocabularies(FunctionalTestCase):

    def test_contact_vocabulary(self):
        Builder('contact').having(
            **{'firstname': u'Sandra',
             'lastname': u'Kaufmann',
             'email': u'sandra.kaufmann@test.ch'}).create()
        Builder('contact').having(
            **{'firstname': u'Elisabeth',
             'lastname': u'K\xe4ppeli',
             'email': 'elisabeth.kaeppeli@test.ch'}).create()

        voca_factory = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.ContactsVocabulary')

        self.assertTerms(
            [('contact:kaufmann-sandra',
              u'Kaufmann Sandra (sandra.kaufmann@test.ch)'),
             ('contact:kappeli-elisabeth',
              u'K\xe4ppeli Elisabeth (elisabeth.kaeppeli@test.ch)')],
            voca_factory(self.portal))

    def test_client_vocabulary_contains_all_active_clients(self):
        create_client(clientid='client1')
        create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)
        set_current_client_id(self.portal)

        voca_factory = getUtility(IVocabularyFactory,
                          name='opengever.ogds.base.ClientsVocabulary')

        self.assertTerms(
            [('client1', 'Client1'), ('client2', 'Client2')],
            voca_factory(self.portal))

    def test_home_dossier_vocabulary_contains_all_open_dossier_from_your_home_client(self):
        class ClientCommunicatorMockUtility(communication.ClientCommunicator):
            implements(communication.IClientCommunicator)

            def get_open_dossiers(self, target_client_id):
                return [{'url': 'http://nohost/client2/op1/op2/dossier1',
                         'path': 'op1/op2/dossier1',
                         'title': 'Dossier 1',
                         'workflow_state': 'dossier-state-active',
                         'reference_number': 'OG 1.2 / 1'},
                        {'url': 'http://nohost/client2/op1/op2/dossier2',
                         'path': 'op1/op2/dossier2',
                         'title': 'Dossier 2',
                         'workflow_state': 'dossier-state-active',
                         'reference_number': 'OG 1.2 / 2'}]

        provideUtility(ClientCommunicatorMockUtility())

        create_client(clientid="client1")
        client2 = create_client(clientid="client2")
        create_ogds_user(TEST_USER_ID, assigned_client=[client2])

        self.portal.REQUEST.set('client', 'client2')

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.HomeDossiersVocabulary')

        self.assertTerms(
            [('op1/op2/dossier1', 'OG 1.2 / 1: Dossier 1'),
             ('op1/op2/dossier2', 'OG 1.2 / 2: Dossier 2')],
            voca_factory(self.portal))

    def test_document_contains_all_documents_of_the_given_remote_dossier(self):

        class ClientCommunicatorMockUtility(communication.ClientCommunicator):

            implements(communication.IClientCommunicator)

            def get_documents_of_dossier(self, target_client_id, dossier_path):
                dossier_url = 'http://nohost/client2/' + dossier_path
                return [{'path': dossier_path + '/document-1',
                         'url': dossier_url + '/document-1',
                         'title': 'First Document',
                         'review_state': 'draft'},
                        {'path': dossier_path + '/document-2',
                         'url': dossier_url + '/document-2',
                         'title': 'Second Document',
                         'review_state': 'draft'}]

        provideUtility(ClientCommunicatorMockUtility())

        create_client(clientid="client1")
        client2 = create_client(clientid="client2")
        create_ogds_user(TEST_USER_ID, assigned_client=[client2])

        self.portal.REQUEST.set('dossier_path', 'op1/op2/dossier2')
        self.portal.REQUEST.set('client', 'client2')

        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.DocumentInSelectedDossierVocabulary')

        self.assertTerms(
            [('op1/op2/dossier2/document-1', 'First Document'),
             ('op1/op2/dossier2/document-2', 'Second Document')],
            voca_factory(self.portal))
