from Products.CMFCore.utils import getToolByName
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.utils import get_current_client
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import obj2brain
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility


class TestContactInfo(FunctionalTestCase):

    def test_current_client_utils(self):
        test_client = create_client(clientid='test_client')
        set_current_client_id(self.portal, clientid='test_client')

        self.assertEquals(u'test_client', get_client_id())
        self.assertEquals(test_client, get_current_client())

    def test_get_clients(self):
        client1 = create_client(clientid='client1')
        client2 = create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)
        set_current_client_id(self.portal, clientid='client1')

        info = getUtility(IContactInformation)

        self.assertEquals([client1, client2], info.get_clients())

    def test_get_clients_for_not_enabled_client(self):
        create_client(clientid='client1')
        create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)
        set_current_client_id(self.portal, clientid='client3')

        info = getUtility(IContactInformation)

        self.assertEquals([], info.get_clients())

    def test_client_by_id(self):
        client1 = create_client(clientid='client1')
        create_client(clientid='client3', enabled=False)

        info = getUtility(IContactInformation)

        self.assertEquals(client1, info.get_client_by_id('client1'))
        self.assertEquals(None, info.get_client_by_id('client3'))
        self.assertEquals(None, info.get_client_by_id('unknown client'))

    def test_is_user(self):
        hugo_boss = create_ogds_user('hugo.boss')

        info = getUtility(IContactInformation)

        self.assertTrue(info.is_user(hugo_boss.userid))
        self.assertFalse(info.is_user(u'inbox:client1'))

    def test_list_user(self):
        create_ogds_user('hugo.boss')
        create_ogds_user('peter.muster')
        create_ogds_user('hanspeter.linder')

        info = getUtility(IContactInformation)

        self.assertEquals(
            [u'hugo.boss', u'peter.muster', u'hanspeter.linder'],
            [u.userid for u in info.list_users()])

    def test_get_user(self):
        hugo_boss = create_ogds_user('hugo.boss')

        info = getUtility(IContactInformation)

        self.assertEquals(hugo_boss.userid, info.get_user('hugo.boss').userid)

        self.assertEquals(None, info.get_user('someone.unknown'))

        with self.assertRaises(ValueError) as cm:
            info.get_user('inbox:client1')
        self.assertEquals(
            'principal inbox:client1 is not a user',
            str(cm.exception))

    def test_describe_user(self):
        create_ogds_user('hugo.boss',
                         **{'firstname': 'Hugo',
                          'lastname': 'Boss',
                          'email': 'hugo@boss.local',
                          'email2': 'hugo@private.ch'})

        info = getUtility(IContactInformation)

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

    def test_describe_pas_user(self):
        mtool = getToolByName(self.portal, 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        member.setMemberProperties(mapping={"fullname": "User Test"})

        info = getUtility(IContactInformation)

        # Test describe with a PAS user:
        self.assertEquals(
            'User Test (test_user_1_)', info.describe(TEST_USER_ID))
        self.assertEquals(
            'User Test', info.describe('test_user_1_', with_principal=False))
        self.assertEquals(
            u'non-existing-user', info.describe('non-existing-user'))

    def test_get_email_from_user(self):
        create_ogds_user('hugo.boss',
                 **{'firstname': 'Hugo',
                  'lastname': 'Boss',
                  'email': 'hugo@boss.local',
                  'email2': 'hugo@private.ch'})

        info = getUtility(IContactInformation)

        self.assertEquals(u'hugo@boss.local',
                          info.get_email('hugo.boss'))
        self.assertEquals(u'hugo@boss.local',
                          info.get_email(info.get_user('hugo.boss')))

        self.assertEquals(u'hugo@private.ch',
                          info.get_email2('hugo.boss'))
        self.assertEquals(u'hugo@private.ch',
                          info.get_email2(info.get_user('hugo.boss')))

    def test_get_profile_url(self):
        create_ogds_user('hugo.boss')

        info = getUtility(IContactInformation)

        self.assertEquals(
            u'http://nohost/plone/@@user-details/hugo.boss',
            info.get_profile_url('hugo.boss'))

    def test_render_link(self):
        create_ogds_user('hugo.boss',
                 **{'firstname': 'Hugo',
                    'lastname': 'Boss', })

        info = getUtility(IContactInformation)

        self.assertEquals(
            u'<a href="http://nohost/plone/@@user-details/hugo.boss">Boss Hugo (hugo.boss)</a>',
            info.render_link('hugo.boss'))

    def test_list_contacts(self):
        Builder('contact').with_metadata(
            **{'firstname': u'Sandra',
             'lastname': u'Kaufmann',
             'email': u'sandra.kaufmann@test.ch'}).create()
        Builder('contact').with_metadata(
            **{'firstname': u'Elisabeth',
             'lastname': u'K\xe4ppeli',
             'email': 'elisabeth.kaeppeli@test.ch'}).create()
        Builder('contact').with_metadata(
            **{'firstname': u'Roger',
             'lastname': u'Wermuth',
             'email': None}).create()

        info = getUtility(IContactInformation)

        self.assertEquals(
            ['kaufmann-sandra', 'kappeli-elisabeth', 'wermuth-roger'],
            [brain.getId for brain in info.list_contacts()])

        self.assertEquals(
            ['contact:kaufmann-sandra',
             'contact:kappeli-elisabeth',
             'contact:wermuth-roger'],
            [contact.contactid for contact in info.list_contacts()])

    def test_is_contact(self):
        info = getUtility(IContactInformation)

        self.assertTrue(info.is_contact('contact:kaufmann-sandra'))
        self.assertFalse(info.is_contact('hugo.boss'))
        self.assertFalse(info.is_contact('inbox:client1'))

    def test_describe_contact(self):
        self.grant('Manager')

        sandra_kaufmann = Builder('contact').with_metadata(
            **{'firstname': u'Sandra',
             'lastname': u'Kaufmann',
             'email': u'sandra.kaufmann@test.ch',
             'email2': u'sandra@test2.ch'}).create()

        info = getUtility(IContactInformation)

        self.assertEquals(u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
                          info.describe(u'contact:kaufmann-sandra'))
        self.assertEquals(
            u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
            info.describe(u'contact:kaufmann-sandra', with_email=True))
        self.assertEquals(
            u'Kaufmann Sandra',
            info.describe(u'contact:kaufmann-sandra', with_principal=False))
        self.assertEquals(
            u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
            info.describe(obj2brain(sandra_kaufmann)))

    def test_get_email_from_contact(self):
        Builder('contact').with_metadata(
            **{'firstname': u'Sandra',
               'lastname': u'Kaufmann',
               'email': u'sandra.kaufmann@test.ch',
               'email2': u'sandra@test2.ch'}).create()

        info = getUtility(IContactInformation)

        self.assertEquals('sandra.kaufmann@test.ch',
                  info.get_email(u'contact:kaufmann-sandra'))

        self.assertEquals(
            'sandra.kaufmann@test.ch',
            info.get_email(info.get_contact('contact:kaufmann-sandra')))

    def test_is_inbox(self):
        info = getUtility(IContactInformation)

        self.assertTrue(info.is_inbox('inbox:client1'))
        self.assertFalse(info.is_inbox('contact:kaufmann-sandra'))
        self.assertFalse(info.is_inbox('hugo.boss'))

    def test_list_inboxes(self):
        create_client(clientid='client1')
        create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)

        info = getUtility(IContactInformation)

        self.assertEquals(
            ((u'inbox:client1', u'Inbox: Client1'),
             (u'inbox:client2', u'Inbox: Client2')),
            tuple(info.list_inboxes()))

    def test_describe_inboxes(self):
        create_client(clientid='client1', title='Client 1')

        info = getUtility(IContactInformation)

        self.assertEquals(
            u'Inbox: Client 1',
            info.describe(u'inbox:client1'))

        self.assertEquals(
            u'Inbox: Client 1',
            info.describe(u'inbox:client1', with_principal=False))

    def test_list_assigned_users(self):
        hugo_boss = create_ogds_user('hugo.boss', groups=('client1_users', ))
        peter_muster = create_ogds_user('hugo.boss', groups=('client2_users', ))
        hanspeter_linder = create_ogds_user(
            'hanspeter.linder', groups=('client1_users', 'client2_users'))

        create_client(clientid='client1')
        create_client(clientid='client2')

        set_current_client_id(self.portal)

        info = getUtility(IContactInformation)

        # list_assigned_users
        self.assertEquals(
            [hanspeter_linder.userid, hugo_boss.userid],
            [user.userid for user in info.list_assigned_users()])

        self.assertEquals(
            [hanspeter_linder.userid, peter_muster.userid],
            [user.userid for user in info.list_assigned_users(client_id='client2')])

    def test_is_client_assigned(self):
        create_ogds_user('hugo.boss', groups=('client1_users', ))
        create_client(clientid='client1')
        create_client(clientid='client2')

        info = getUtility(IContactInformation)

        # is_client_assigned
        self.assertFalse(
            info.is_client_assigned(userid='hugo.boss', client_id='client2'))
        self.assertTrue(
            info.is_client_assigned(userid='hugo.boss', client_id='client1'))

    def test_get_assigned_clients(self):
        create_ogds_user('hugo.boss', groups=('client1_users', ))
        create_ogds_user('hanspeter.linder', groups=('client1_users', 'client2_users'))
        client1 = create_client(clientid='client1')
        client2 = create_client(clientid='client2')

        info = getUtility(IContactInformation)

        self.assertEquals(
            [client1, ],
            info.get_assigned_clients(userid='hugo.boss'))

        self.assertEquals(
            [client1, client2],
            info.get_assigned_clients(userid='hanspeter.linder'))

    def test_list_group_users(self):
        hanspeter_linder = create_ogds_user(
            'hanspeter.linder', groups=('client1_users', 'client2_users'))
        peter_muster = create_ogds_user('peter.muster', groups=('client1_users', ))

        info = getUtility(IContactInformation)

        self.assertEquals(
            [hanspeter_linder.userid, peter_muster.userid],
            [user.userid for user in info.list_group_users('client1_users')])

        self.assertEquals([],
                          list(info.list_group_users('not_existing_groupid')))

    def test_list_users_group(self):
        create_ogds_user('hugo.boss', groups=('client1_users', 'client1_inbox_users'))

        info = getUtility(IContactInformation)

        self.assertEquals(
            ['client1_users', 'client1_inbox_users'],
            [group.groupid for group in info.list_user_groups('hugo.boss')])

    def test_is_user_in_inbox_group(self):
        create_ogds_user('hugo.boss', groups=('client1_inbox_users', ))
        create_ogds_user('hanspeter.linder',
                         groups=('client1_inbox_users', 'client2_inbox_users'))

        create_client(clientid='client1', inbox_group='client1_inbox_users')
        create_client(clientid='client2', inbox_group='client2_inbox_users')

        info = getUtility(IContactInformation)

        self.assertTrue(info.is_user_in_inbox_group(
            userid='hugo.boss', client_id='client1'))
        self.assertFalse(info.is_user_in_inbox_group(
            userid='hugo.boss', client_id='client2'))
        self.assertTrue(info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='client1'))
        self.assertTrue(info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='client2'))
        self.assertFalse(info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='notexists'))

    def test_is_group_member(self):
        create_ogds_user('hugo.boss', groups=('client1_inbox_users', ))
        create_ogds_user('hanspeter.linder',
                         groups=('client2_inbox_users'))

        info = getUtility(IContactInformation)

        self.assertTrue(
            info.is_group_member(u'client1_inbox_users', u'hugo.boss'))
        self.assertFalse(
            info.is_group_member(u'client1_inbox_users', u'hanspeter.linder'))

    def test_user_sort_dict(self):
        create_client(clientid='client1')
        create_client(clientid='client2')
        create_ogds_user('hugo.boss', **{'firstname': 'Hugo', 'lastname': 'Boss'})
        create_ogds_user('peter.muster', **{'firstname': 'Peter', 'lastname': 'Muster'})

        info = getUtility(IContactInformation)

        # check the sort dictionaries
        self.assertEquals(
            {u'inbox:client1': u'Inbox: Client1',
             u'hugo.boss': u'Boss Hugo',
             u'inbox:client2': u'Inbox: Client2',
             u'peter.muster': u'Muster Peter'},
            info.get_user_sort_dict())

    def test_user_contact_sort_dict(self):
        create_client(clientid='client1')
        create_client(clientid='client2')
        create_ogds_user('hugo.boss', **{'firstname': 'Hugo', 'lastname': 'Boss'})
        create_ogds_user('peter.muster', **{'firstname': 'Peter', 'lastname': 'Muster'})
        Builder('contact').with_metadata(
            **{'firstname': u'Sandra',
               'lastname': u'Kaufmann',
               'email': u'sandra.kaufmann@test.ch'}).create()
        Builder('contact').with_metadata(
            **{'firstname': u'Elisabeth',
               'lastname': u'K\xe4ppeli',
               'email': 'elisabeth.kaeppeli@test.ch'}).create()

        info = getUtility(IContactInformation)

        self.assertEquals(
            {u'inbox:client1': u'Inbox: Client1',
             'contact:kaufmann-sandra': u'Kaufmann Sandra',
             'contact:kappeli-elisabeth': u'K\xe4ppeli Elisabeth',
             u'hugo.boss': u'Boss Hugo',
             u'inbox:client2': u'Inbox: Client2',
             u'peter.muster': u'Muster Peter'},
            info.get_user_contact_sort_dict())
