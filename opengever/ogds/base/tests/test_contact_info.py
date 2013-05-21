# from opengever.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.testing import create_contacts
from opengever.ogds.base.utils import create_session, get_current_client
from opengever.ogds.base.utils import get_client_id
from opengever.testing import FunctionalTestCase
from opengever.testing import set_current_client_id
from zope.component import getUtility


class TestContactInfo(FunctionalTestCase):

    def test_contact_info(self):
        set_current_client_id(self.portal)

        # Lets create some users:
        session = create_session()

        hugo_boss = _create_example_user(session, self.portal,
                             'hugo.boss',
                             {'firstname': 'Hugo',
                              'lastname': 'Boss',
                              'email': 'hugo@boss.local',
                              'email2': 'hugo@private.ch'},
                             ('client1_users',
                              'client1_inbox_users'))

        peter_muster =_create_example_user(session, self.portal,
                             'peter.muster',
                             {'firstname': 'Peter',
                              'lastname': 'Muster'},
                             ('client2_users',
                              'client2_inbox_users'))

        hanspeter_linder = _create_example_user(session, self.portal,
                             'hanspeter.linder',
                             {'firstname': 'hanspeter',
                              'lastname': 'linder'},
                             ('client2_users', 'client1_users'))

        _create_example_user(session, self.portal,
                             'robin.hood',
                             {'firstname': 'Robin',
                              'active' : '0',
                              'lastname': 'Hood'},
                             [])


        # And we also need some clients:
        client1 = _create_example_client(session, 'client1',
                           {'title': 'Client 1',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://nohost/client1',
                            'public_url': 'http://nohost/client1',
                            'group': 'client1_users',
                            'inbox_group': 'client1_inbox_users'})

        client2 = _create_example_client(session, 'client2',
                           {'title': 'Client 2',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://nohost/client2',
                            'public_url': 'http://nohost/client2',
                            'group': 'client2_users',
                            'inbox_group': 'client2_inbox_users'})

        # the ip_address column should also work with a comma seperated list
        _create_example_client(session, 'client3',
                           {'title': 'Client 3',
                            'enabled': False,
                            'ip_address': '127.0.0.1,192.168.1.2',
                            'site_url': 'http://nohost/client3',
                            'public_url': 'http://nohost/client3',
                            'group': 'client3_users',
                            'inbox_group': 'client3_inbox_users'})

        # Create some local contacts:
        create_contacts(self.portal)
        self.assertEquals(3, len(self.portal.contacts.objectIds()))

        # Get the current client (see layer testing.py):
        self.assertEquals(u'client1', get_client_id())

        self.assertEquals(client1, get_current_client())

        # Get the contact information utlity:
        info = getUtility(IContactInformation)


        # User tests:
        self.assertEquals(4, len(info.list_users()))

        self.assertEquals(
            [u'hugo.boss', u'peter.muster', u'hanspeter.linder', u'robin.hood'],
            [u.userid for u in info.list_users()]
        )

        self.assertTrue(info.is_user('hugo.boss'))
        self.assertFalse(info.is_contact('hugo.boss'))
        self.assertFalse(info.is_inbox('hugo.boss'))

        self.assertEquals(hugo_boss.userid,
                          info.get_user('hugo.boss').userid)
        self.assertEquals(None, info.get_user('someone.unknown'))

        with self.assertRaises(ValueError) as cm:
            info.get_user('inbox:client1')

        self.assertEquals(
            'principal inbox:client1 is not a user',
            str(cm.exception))

        self.assertEquals(u'Boss Hugo (hugo.boss)',
                          info.describe('hugo.boss'))

        self.assertEquals(u'Boss Hugo (hugo.boss, hugo@boss.local)',
                          info.describe('hugo.boss', with_email=True))

        self.assertEquals(u'Boss Hugo',
                          info.describe('hugo.boss', with_principal=False))

        self.assertEquals(
            u'Boss Hugo (hugo@boss.local)',
            info.describe('hugo.boss', with_email=True, with_principal=False))

        self.assertEquals(u'Boss Hugo (hugo.boss)',
            info.describe(info.get_user('hugo.boss')))

        self.assertEquals(u'hugo@boss.local',
                          info.get_email('hugo.boss'))
        self.assertEquals(u'hugo@boss.local',
                          info.get_email(info.get_user('hugo.boss')))

        self.assertEquals(u'hugo@private.ch',
                          info.get_email2('hugo.boss'))
        self.assertEquals(u'hugo@private.ch',
                          info.get_email2(info.get_user('hugo.boss')))

        self.assertEquals(
            u'http://nohost/plone/@@user-details/hugo.boss',
            info.get_profile_url('hugo.boss'))

        self.assertEquals(
            u'<a href="http://nohost/plone/@@user-details/hugo.boss">Boss Hugo (hugo.boss)</a>',
            info.render_link('hugo.boss'))

        # Contacts tests:

        contacts = info.list_contacts()
        # contacts
        # [<Products.ZCatalog.Catalog.mybrains object at ...>, <Products.ZCatalog.Catalog.mybrains object at ...>, <Products.ZCatalog.Catalog.mybrains object at ...>]

        self.assertEquals('contact:kaufmann-sandra', contacts[0].contactid)

        self.assertTrue(info.is_contact('contact:kaufmann-sandra'))

        sandra = info.get_contact('contact:kaufmann-sandra')
        # sandra
        # <Products.ZCatalog.Catalog.mybrains object at ...>

        self.assertEquals(u'Sandra', sandra.firstname)
        self.assertEquals(u'Kaufmann', sandra.lastname)
        self.assertEquals('sandra.kaufmann@test.ch', sandra.email)
        self.assertEquals(u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
                          info.describe('contact:kaufmann-sandra'))

        self.assertEquals(u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
                          info.describe(u'contact:kaufmann-sandra'))
        self.assertEquals(
            u'Kaufmann Sandra',
            info.describe(u'contact:kaufmann-sandra', with_principal=False))



        self.assertEquals(u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
                          info.describe(contacts[0]))

        self.assertEquals('sandra.kaufmann@test.ch',
                          info.get_email(u'contact:kaufmann-sandra'))

        self.assertEquals(
            'sandra.kaufmann@test.ch',
            info.get_email(info.get_contact('contact:kaufmann-sandra')))

        # Inboxes tests:
        self.assertEquals(
            ((u'inbox:client1', u'Inbox: Client 1'), (u'inbox:client2', u'Inbox: Client 2')),
            tuple(info.list_inboxes())
        )

        self.assertTrue(info.is_inbox(u'inbox:client1'))
        self.assertFalse(info.is_user(u'inbox:client1'))
        self.assertFalse(info.is_contact(u'inbox:client1'))

        self.assertEquals(
            client1,
            info.get_client_of_inbox(u'inbox:client1'))

        self.assertEquals(
            u'client1_inbox_users',
            info.get_group_of_inbox(u'inbox:client1'))

        self.assertEquals(
            u'Inbox: Client 1',
            info.describe(u'inbox:client1'))

        self.assertEquals(
            u'Inbox: Client 1',
            info.describe(u'inbox:client1', with_principal=False))

        # Various lists and other methods:
        self.assertEquals(
            [hanspeter_linder.userid, hugo_boss.userid],
            [user.userid for user in info.list_assigned_users()])

        self.assertEquals(
            [hanspeter_linder.userid, peter_muster.userid],
            [user.userid for user in info.list_assigned_users(client_id='client2')])

        self.assertEquals(
            [client1, ],
            list(info.get_assigned_clients(userid='hugo.boss')))

        self.assertEquals(
            [client1, client2],
            list(info.get_assigned_clients(userid='hanspeter.linder')))

        self.assertFalse(
            info.is_client_assigned(userid='hugo.boss', client_id='client2'))

        self.assertTrue(
            info.is_client_assigned(userid='hugo.boss', client_id='client1'))

        self.assertEquals(
            [hanspeter_linder.userid, peter_muster.userid],
            [user.userid for user in info.list_group_users('client2_users')])

        self.assertEquals([],
                          list(info.list_group_users('not_existing_groupid')))

        self.assertEquals(
            [client1, client2],
            list(info.get_clients()))

        self.assertEquals(client1, info.get_client_by_id('client1'))

        self.assertEquals(None, info.get_client_by_id('client3'))

        self.assertEquals(None, info.get_client_by_id('unknown client'))

        self.assertEquals(
            ['client1_users', 'client1_inbox_users'],
            [group.groupid for group in info.list_user_groups('hugo.boss')])

        self.assertTrue(info.is_user_in_inbox_group(
            userid='hugo.boss', client_id='client1'))

        self.assertFalse(info.is_user_in_inbox_group(
            userid='hugo.boss', client_id='client2'))

        self.assertFalse(info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='client1'))

        self.assertFalse(info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='notexists'))

        self.assertTrue(
            info.is_group_member(u'client1_inbox_users', u'hugo.boss'))

        self.assertFalse(
            info.is_group_member(u'client1_inbox_users', u'hanspeter.linder'))


        # check the sort dictionaries
        self.assertEquals(
            {u'inbox:client1': u'Inbox: Client 1',
             u'robin.hood': u'Hood Robin',
             u'hugo.boss': u'Boss Hugo',
             u'inbox:client2': u'Inbox: Client 2',
             u'hanspeter.linder': u'linder hanspeter',
             u'peter.muster': u'Muster Peter'},
            info.get_user_sort_dict())

        self.assertEquals(
            {u'inbox:client1': u'Inbox: Client 1',
             'contact:wermuth-roger': u'Wermuth Roger',
             u'robin.hood': u'Hood Robin',
             'contact:kaufmann-sandra': u'Kaufmann Sandra',
             'contact:kappeli-elisabeth': u'K\xe4ppeli Elisabeth',
             u'hugo.boss': u'Boss Hugo',
             u'inbox:client2': u'Inbox: Client 2',
             u'hanspeter.linder': u'linder hanspeter',
             u'peter.muster': u'Muster Peter'},
            info.get_user_contact_sort_dict())

        # Test describe with a PAS user:
        self.assertEquals(
                ' (test_user_1_)',
                info.describe('test_user_1_'))

        self.assertEquals('', info.describe('test_user_1_', with_principal=False))

        self.assertEquals(u'non-existing-user',
                          info.describe('non-existing-user'))
