from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.utils import get_current_client
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import obj2brain
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility


class TestClientUtils(FunctionalTestCase):

    def setUp(self):
        super(TestClientUtils, self).setUp()

        self.test_client = create_client(clientid='test_client')
        set_current_client_id(self.portal, clientid='test_client')

    def test_get_client_id_returns_current_client_id(self):
        self.assertEquals(u'test_client', get_client_id())

    def test_get_current_client_returns_current_client_object(self):
        self.assertEquals(self.test_client, get_current_client())


class TestClientHelpers(FunctionalTestCase):

    def setUp(self):
        super(TestClientHelpers, self).setUp()
        self.info = getUtility(IContactInformation)

        self.client1 = create_client(clientid='client1')
        self.client2 = create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)
        set_current_client_id(self.portal, clientid='client1')

    def test_get_clients_returns_all_enabled_clients(self):
        self.assertEquals([self.client1, self.client2], self.info.get_clients())

    def test_get_clients_returns_empty_list_when_current_client_is_not_enabled(self):
        set_current_client_id(self.portal, clientid='client3')

        self.assertEquals([], self.info.get_clients())

    def test_get_client_by_id_for_exsiting_client_returns_client(self):
        self.assertEquals(self.client1, self.info.get_client_by_id('client1'))

    def test_get_client_by_id_for_disabled_client_returns_none(self):
        self.assertEquals(None, self.info.get_client_by_id('unknown client'))

    def test_get_client_by_id_for_not_existing_client_returns_none(self):
        self.assertEquals(None, self.info.get_client_by_id('unknown client'))

    def test_list_assigned_users_returns_all_ogds_user_objects(self):
        hugo_boss = create_ogds_user('hugo.boss', groups=('client1_users', ))
        peter_muster = create_ogds_user('hugo.boss', groups=('client2_users', ))
        hanspeter_linder = create_ogds_user(
            'hanspeter.linder', groups=('client1_users', 'client2_users'))

        self.assertEquals(
            [hugo_boss.userid, hanspeter_linder.userid],
            [user.userid for user in self.info.list_assigned_users()])

        self.assertEquals(
            [peter_muster.userid, hanspeter_linder.userid],
            [user.userid for user in self.info.list_assigned_users(client_id='client2')])

    def test_user_is_assigned_to_client_if_he_is_in_the_client_users_group(self):
        create_ogds_user('hugo.boss', groups=('client1_users', ))

        self.assertFalse(
            self.info.is_client_assigned(userid='hugo.boss', client_id='client2'))
        self.assertTrue(
            self.info.is_client_assigned(userid='hugo.boss', client_id='client1'))

    def test_get_assigned_clients_returns_all_clients_wich_the_users_is_in_the_clients_usergroup(self):
        create_ogds_user('hugo.boss', groups=('client1_users', ))
        create_ogds_user('hanspeter.linder', groups=('client1_users', 'client2_users'))

        self.assertEquals(
            [self.client1, ],
            self.info.get_assigned_clients(userid='hugo.boss'))

        self.assertEquals(
            [self.client1, self.client2],
            self.info.get_assigned_clients(userid='hanspeter.linder'))


class TestUserHelpers(FunctionalTestCase):

    def setUp(self):
        super(TestUserHelpers, self).setUp()
        self.info = getUtility(IContactInformation)

    def test_list_user_returns_all_users_ogds_objects(self):
        create_ogds_user('hugo.boss')
        create_ogds_user('peter.muster')
        create_ogds_user('hanspeter.linder')

        self.assertEquals(
            [u'hugo.boss', u'peter.muster', u'hanspeter.linder'],
            [u.userid for u in self.info.list_users()])

    def test_get_user_returns_sql_user_obj_when_he_exists(self):
        hugo_boss = create_ogds_user('hugo.boss')

        self.assertEquals(hugo_boss.userid, self.info.get_user('hugo.boss').userid)

    def test_get_user_returns_none_when_the_user_dont_exists(self):
        self.assertEquals(None, self.info.get_user('someone.unknown'))

    def test_get_user_raise_if_the_user_is_a_inbox(self):
        with self.assertRaises(ValueError) as cm:
            self.info.get_user('inbox:client1')
        self.assertEquals(
            'principal inbox:client1 is not a user',
            str(cm.exception))

    def test_getting_profile_url_returns_user_detail_view_url(self):
        create_ogds_user('hugo.boss')

        self.assertEquals(
            u'http://nohost/plone/@@user-details/hugo.boss',
            self.info.get_profile_url('hugo.boss'))

    def test_render_link_returns_user_details_link(self):
        create_ogds_user('hugo.boss',
                 **{'firstname': 'Hugo',
                    'lastname': 'Boss', })

        self.assertEquals(
            u'<a href="http://nohost/plone/@@user-details/hugo.boss">Boss Hugo (hugo.boss)</a>',
            self.info.render_link('hugo.boss'))


class TestEmailGetter(FunctionalTestCase):

    def setUp(self):
        super(TestEmailGetter, self).setUp()
        self.info = getUtility(IContactInformation)

    def test_get_email_for_a_user_return_his_first_email(self):
        create_ogds_user('hugo.boss', **{'firstname': 'Hugo',
                                        'lastname': 'Boss',
                                        'email': 'hugo@boss.local',
                                        'email2': 'hugo@private.ch'})

        self.assertEquals(u'hugo@boss.local',
                          self.info.get_email('hugo.boss'))
        self.assertEquals(u'hugo@boss.local',
                          self.info.get_email(self.info.get_user('hugo.boss')))

    def test_get_email2_for_a_user_return_his_second_email(self):
        create_ogds_user('hugo.boss', **{'firstname': 'Hugo',
                                'lastname': 'Boss',
                                'email': 'hugo@boss.local',
                                'email2': 'hugo@private.ch'})

        self.assertEquals(u'hugo@private.ch',
                          self.info.get_email2('hugo.boss'))

        self.assertEquals(u'hugo@private.ch',
                          self.info.get_email2(self.info.get_user('hugo.boss')))

    def test_get_email_for_a_contact_return_his_email(self):
        create(Builder('contact')
               .having(**{'firstname': u'Sandra',
                          'lastname': u'Kaufmann',
                          'email': u'sandra.kaufmann@test.ch',
                          'email2': u'sandra@test2.ch'}))

        self.assertEquals('sandra.kaufmann@test.ch',
                  self.info.get_email(u'contact:kaufmann-sandra'))
        self.assertEquals(
            'sandra.kaufmann@test.ch',
            self.info.get_email(self.info.get_contact('contact:kaufmann-sandra')))

    def test_get_email2_for_a_contact_return_his_second_email(self):
        create(Builder('contact')
               .having(**{'firstname': u'Sandra',
                          'lastname': u'Kaufmann',
                          'email': u'sandra.kaufmann@test.ch',
                          'email2': u'sandra@test2.ch'}))

        self.assertEquals('sandra@test2.ch',
                          self.info.get_email2(u'contact:kaufmann-sandra'))

    def test_get_email_for_a_inbox_return_none(self):
        self.assertEquals(
            None, self.info.get_email(u'inbox:client1'))

        self.assertEquals(
            None, self.info.get_email2(u'inbox:client1'))


class TestGroupHelpers(FunctionalTestCase):

    def setUp(self):
        super(TestGroupHelpers, self).setUp()
        self.info = getUtility(IContactInformation)

        self.client1 = create_client(clientid='client1')
        self.client2 = create_client(clientid='client2')
        set_current_client_id(self.portal)

    def test_list_group_users_returns_all_users_assigned_to_this_group(self):
        hanspeter_linder = create_ogds_user(
            'hanspeter.linder', groups=('client1_users', 'client2_users'))
        peter_muster = create_ogds_user('peter.muster', groups=('client1_users', ))

        self.assertEquals(
            [hanspeter_linder.userid, peter_muster.userid],
            [user.userid for user in self.info.list_group_users('client1_users')])

        self.assertEquals([],
                          list(self.info.list_group_users('not_existing_groupid')))

    def test_list_users_group_returns_a_list_of_all_group_ids_the_user_is_assigned(self):
        create_ogds_user('hugo.boss', groups=('client1_users', 'client1_inbox_users'))

        self.assertEquals(
            ['client1_users', 'client1_inbox_users'],
            [group.groupid for group in self.info.list_user_groups('hugo.boss')])

    def test_user_is_inbox_group_when_he_is_in_the_inbox_group_of_the_given_client(self):
        create_ogds_user('hugo.boss', groups=('client1_inbox_users', ))
        create_ogds_user('hanspeter.linder',
                         groups=('client1_inbox_users', 'client2_inbox_users'))

        create_client(clientid='client1', inbox_group='client1_inbox_users')
        create_client(clientid='client2', inbox_group='client2_inbox_users')

        self.assertTrue(self.info.is_user_in_inbox_group(
            userid='hugo.boss', client_id='client1'))
        self.assertFalse(self.info.is_user_in_inbox_group(
            userid='hugo.boss', client_id='client2'))

        self.assertTrue(self.info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='client1'))
        self.assertTrue(self.info.is_user_in_inbox_group(
            userid='hanspeter.linder', client_id='client2'))


class TestContactInfoOGDSUserDescription(FunctionalTestCase):

    def setUp(self):
        super(TestContactInfoOGDSUserDescription, self).setUp()
        self.info = getUtility(IContactInformation)

        self.hugo_boss = create_ogds_user('hugo.boss',
                         **{'firstname': 'Hugo',
                            'lastname': 'Boss',
                            'email': 'hugo@boss.local',
                            'email2': 'hugo@private.ch'})

    def test_default_contains_fullname_and_userid_in_parentheses(self):
        self.assertEquals(u'Boss Hugo (hugo.boss)',
                          self.info.describe('hugo.boss'))

        self.assertEquals(u'Boss Hugo (hugo.boss)',
                          self.info.describe(self.info.get_user('hugo.boss')))

    def test_with_email_options_contains_fullname_and_userid_and_email_in_parentheses(self):
        self.assertEquals(
            u'Boss Hugo (hugo.boss, hugo@boss.local)',
            self.info.describe('hugo.boss', with_email=True))

    def test_without_principal_contains_only_fullname(self):
        self.assertEquals(
            u'Boss Hugo',
            self.info.describe('hugo.boss', with_principal=False))

    def test_without_principal_with_email_contains_fullname_and_email_address_in_parentheses(self):
        self.assertEquals(
            u'Boss Hugo (hugo@boss.local)',
            self.info.describe('hugo.boss', with_email=True, with_principal=False))


class TestContactInfoPASUserDescription(FunctionalTestCase):

    def setUp(self):
        super(TestContactInfoPASUserDescription, self).setUp()
        self.info = getUtility(IContactInformation)

        mtool = getToolByName(self.portal, 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        member.setMemberProperties(mapping={"fullname": "User Test"})

    def test_default_contains_fullname_and_userid_in_parentheses(self):
        self.assertEquals(
            'User Test (test_user_1_)', self.info.describe(TEST_USER_ID))

    def test_without_principal_contains_only_fullname(self):
        self.assertEquals(
            'User Test', self.info.describe('test_user_1_', with_principal=False))

    def test_contains_given_userid_for_a_not_existing_pas_user(self):
        self.assertEquals(
            u'non-existing-user', self.info.describe('non-existing-user'))


class TestContactInfoContactDescription(FunctionalTestCase):

    def setUp(self):
        super(TestContactInfoContactDescription, self).setUp()
        self.info = getUtility(IContactInformation)

        self.sandra_kaufmann = create(
            Builder('contact')
            .having(**{'firstname': u'Sandra',
                       'lastname': u'Kaufmann',
                       'email': u'sandra.kaufmann@test.ch',
                       'email2': u'sandra@test2.ch'}))

    def test_default_contains_fullname_and_email_in_parentheses(self):
        self.grant('Manager')
        self.assertEquals(
            u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
            self.info.describe(u'contact:kaufmann-sandra'))

        self.assertEquals(
            u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
            self.info.describe(obj2brain(self.sandra_kaufmann)))

    def test_with_email_contains_fullname_and_email_in_parentheses(self):
        self.assertEquals(
            u'Kaufmann Sandra (sandra.kaufmann@test.ch)',
            self.info.describe(u'contact:kaufmann-sandra', with_email=True))

    def test_without_principal_contains_only_fullname(self):
        self.assertEquals(
            u'Kaufmann Sandra',
            self.info.describe(u'contact:kaufmann-sandra', with_principal=False))


class TestContactInfoAdditionals(FunctionalTestCase):

    def setUp(self):
        super(TestContactInfoAdditionals, self).setUp()
        self.info = getUtility(IContactInformation)

    def test_contacts_or_inboxes_is_not_a_user(self):
        self.assertFalse(self.info.is_user(u'inbox:client1'))
        self.assertFalse(self.info.is_user(u'contact:kaufmann-sandra'))

    def test_all_possibly_valid_userids_are_a_user(self):
        self.assertTrue(self.info.is_user('hugo.boss'))
        self.assertTrue(self.info.is_user('peter.muster'))

    def test_only_prinicpal_prefixed_with_contact_and_colon_is_contact(self):
        self.assertTrue(self.info.is_contact('contact:kaufmann-sandra'))
        self.assertFalse(self.info.is_contact('kaufmann-sandra'))
        self.assertFalse(self.info.is_contact('inbox:client1'))

    def test_only_prinicpal_prefixed_with_inbox_and_colon_is_a_inbox(self):
        self.assertTrue(self.info.is_inbox('inbox:client1'))
        self.assertFalse(self.info.is_inbox('contact:kaufmann-sandra'))
        self.assertFalse(self.info.is_inbox('hugo.boss'))

    def test_list_contacts_return_all_contact_brains(self):
        create(Builder('contact')
               .having(**{'firstname': u'Sandra',
                          'lastname': u'Kaufmann',
                          'email': u'sandra.kaufmann@test.ch'}))
        create(Builder('contact')
               .having(**{'firstname': u'Elisabeth',
                          'lastname': u'K\xe4ppeli',
                          'email': 'elisabeth.kaeppeli@test.ch'}))
        create(Builder('contact')
               .having(**{'firstname': u'Roger',
                          'lastname': u'Wermuth',
                          'email': None}))

        self.assertEquals(
            ['kaufmann-sandra', 'kappeli-elisabeth', 'wermuth-roger'],
            [brain.getId for brain in self.info.list_contacts()])

        self.assertEquals(
            ['contact:kaufmann-sandra',
             'contact:kappeli-elisabeth',
             'contact:wermuth-roger'],
            [contact.contactid for contact in self.info.list_contacts()])

    def test_list_inboxes_returns_a_generator_with_principal_and_description_pairs(self):
        create_client(clientid='client1')
        create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)

        self.assertEquals(
            ((u'inbox:client1', u'Inbox: Client1'),
             (u'inbox:client2', u'Inbox: Client2')),
            tuple(self.info.list_inboxes()))

    def test_describing_inboxes(self):
        create_client(clientid='client1', title='Client 1')

        self.assertEquals(
            u'Inbox: Client 1',
            self.info.describe(u'inbox:client1'))

        self.assertEquals(
            u'Inbox: Client 1',
            self.info.describe(u'inbox:client1', with_principal=False))
