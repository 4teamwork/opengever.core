from ftw.builder import Builder
from ftw.builder import create
from ftw.solr.connection import SolrResponse
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.schema import SolrSchema
from mock import MagicMock
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.sources import AllEmailContactsAndUsersSource
from opengever.ogds.base.sources import AllFilteredGroupsSource
from opengever.ogds.base.sources import AllGroupsSource
from opengever.ogds.base.sources import AllUsersAndGroupsSource
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.ogds.base.sources import AllUsersSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import ContactsSource
from opengever.ogds.base.sources import CurrentAdminUnitOrgUnitsSource
from opengever.ogds.base.sources import UsersContactsInboxesSource
from opengever.ogds.models.group import Group
from opengever.sharing.interfaces import ISharingConfiguration
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from pkg_resources import resource_string
from plone import api
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
import os


class SolrMockupTestCase(IntegrationTestCase):

    features = ('solr', )
    schema = None
    search = None

    def setUp(self):
        super(SolrMockupTestCase, self).setUp()
        assert self.schema is not None, 'A path for Solr schema is needed'
        conn = MagicMock(name='SolrConnection')
        conn.get = MagicMock(
            name='get',
            return_value=SolrResponse(
                body=self.schema,
                status=200,
            ))

        manager = MagicMock(name='SolrConnectionManager')
        manager.connection = conn
        manager.schema = SolrSchema(manager)

        solr = getUtility(ISolrSearch)
        solr._manager = manager

        assert self.search is not None, 'A path for Solr search is needed'
        solr.search = MagicMock(
            name='search',
            return_value=SolrResponse(
                body=self.search,
                status=200,
            ))
        self.solr = solr
        self.source = UsersContactsInboxesSource(self.portal)


class TestUsersContactsInboxesSourceInt(SolrMockupTestCase):

    schema = resource_string(
        'opengever.ogds.base.tests',
        os.path.join(
            'data',
            'solr_user_contacts_inboxes_source_schema.json'),
    )
    search = resource_string(
        'opengever.ogds.base.tests',
        os.path.join(
            'data',
            'solr_user_contacts_inboxes_source_search.json'),
    )

    def setUp(self):
        super(TestUsersContactsInboxesSourceInt, self).setUp()
        self.source = UsersContactsInboxesSource(self.portal)

    def test_contacts_appear_in_solr_result(self):
        query_string = u'B\xc3\xbcu'
        terms = self.source.search(query_string)
        self.assertEquals([u'Lehner-Baum\xe4nn Maria (m@r.ia)'],
                          [term.title for term in terms])
        self.assertEquals([u'contact:lehner-baumann-maria'],
                          [term.value for term in terms])


class TestAllEmailContactsAndUsersSourceInt(SolrMockupTestCase):

    schema = resource_string(
        'opengever.ogds.base.tests',
        os.path.join(
            'data',
            'solr_all_email_contacts_and_users_source_schema.json'),
    )
    search = resource_string(
        'opengever.ogds.base.tests',
        os.path.join(
            'data',
            'solr_all_email_contacts_and_users_source_search.json'),
    )

    def setUp(self):
        super(TestAllEmailContactsAndUsersSourceInt, self).setUp()
        self.source = AllEmailContactsAndUsersSource(self.portal)

    def test_contacts_appear_in_solr_result(self):
        query_string = u'B\xc3\xbcu'
        terms = self.source.search(query_string)
        self.assertEquals([u'Lehner-Baum\xe4nn Maria (m@r.ia)'],
                          [term.title for term in terms])
        self.assertEquals([u'm@r.ia:lehner-baumann-maria'],
                          [term.value for term in terms])


class TestAllUsersInboxesAndTeamsSource(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestAllUsersInboxesAndTeamsSource, self).setUp()

        self.admin_unit = create(Builder('admin_unit'))
        self.org_unit1 = create(Builder('org_unit')
                                .id('org-unit-1')
                                .having(title=u'Informatik',
                                        admin_unit=self.admin_unit)
                                .with_default_groups())
        self.org_unit2 = create(Builder('org_unit')
                                .id('org-unit-2')
                                .having(title=u'Finanzdirektion',
                                        admin_unit=self.admin_unit)
                                .with_default_groups())

        self.disabled_unit = create(Builder('org_unit')
                                    .id('org-unit-3')
                                    .having(title=u'Steueramt',
                                            enabled=False,
                                            admin_unit=self.admin_unit)
                                    .with_default_groups())

        self.john = create(Builder('ogds_user')
                           .id('john')
                           .having(firstname=u'John', lastname=u'Doe')
                           .assign_to_org_units([self.org_unit1]))
        self.hugo = create(Builder('ogds_user')
                           .id('hugo')
                           .having(firstname=u'Hugo', lastname=u'Boss')
                           .assign_to_org_units([self.org_unit1]))
        self.hans = create(Builder('ogds_user')
                           .id('hans')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .assign_to_org_units([self.org_unit1,
                                                 self.org_unit2,
                                                 self.disabled_unit]))
        self.reto = create(Builder('ogds_user')
                           .id('reto')
                           .having(firstname=u'Reto', lastname=u'Rageto')
                           .assign_to_org_units([self.org_unit2]))

        self.simon = create(Builder('ogds_user')
                            .id('simon')
                            .having(firstname=u'Simon', lastname=u'Says')
                            .assign_to_org_units([self.disabled_unit]))

        self.source = AllUsersInboxesAndTeamsSource(self.portal)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken(u'org-unit-1:hans')
        self.assertTrue(isinstance(term, SimpleTerm))
        self.assertEquals(u'Informatik: Peter Hans (hans)',
                          term.title)

    def test_get_term_by_token_raises_BadRequest_if_no_token(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken(None)

    def test_get_term_by_token_raises_BadReques_if_token_is_malformed(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('dummy')

    def test_get_term_by_token_raises_LookupError_if_no_result(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('dummy:dummy')

    def test_title_token_and_value_of_term(self):
        result = self.source.search('John')
        self.assertEqual(1, len(result), 'Expect one result. only John')
        self.assertEquals(u'org-unit-1:john', result[0].token)
        self.assertEquals(u'org-unit-1:john', result[0].value)
        self.assertEquals(u'Informatik: Doe John (john)',
                          result[0].title)

    def test_users_in_result_are_ordered_by_user_lastname_and_firstname(self):
        self.john = create(Builder('ogds_user')
                           .id('user1')
                           .having(firstname=u'cccc', lastname=u'aaaa')
                           .assign_to_org_units([self.org_unit1]))

        self.john = create(Builder('ogds_user')
                           .id('user2')
                           .having(firstname=u'bbbbb', lastname=u'aaaa')
                           .assign_to_org_units([self.org_unit1]))

        self.john = create(Builder('ogds_user')
                           .id('user3')
                           .having(firstname=u'YYYY', lastname=u'ZZZZ')
                           .assign_to_org_units([self.org_unit1]))

        self.assertEquals(
            ['inbox:org-unit-1', 'org-unit-1:user2', 'org-unit-1:user1', 'org-unit-1:hugo',
             'org-unit-1:john', 'org-unit-1:hans', 'org-unit-1:user3'],
            [term.token for term in self.source.search('Informatik')])

    def test_search_for_orgunit(self):
        result = self.source.search('Informatik')
        result.pop(0)  # Remove inbox

        self.assertEquals(3, len(result), 'Expect 3 items')
        self.assertTermKeys([u'org-unit-1:hans', u'org-unit-1:hugo', u'org-unit-1:john'],
                            result)

    def test_search_for_inbox(self):
        result = self.source.search('inbox:org-unit-1')

        self.assertEquals(1, len(result), 'Expect 1 item')
        self.assertTermKeys([u'inbox:org-unit-1'], result)

    def test_return_no_search_result_for_inactive_orgunits(self):
        result = self.source.search('Steueramt')

        self.assertFalse(result,
                         'Expect no result, since the Steueramt is disabled')

    def test_user_is_once_per_active_orgunit_in_resultset(self):
        result = self.source.search('Hans')

        self.assertEquals(2, len(result), 'Expect 3 items')
        self.assertTermKeys([u'org-unit-1:hans', u'org-unit-2:hans'], result)

    def test_source_length_is_length_of_search_result(self):
        self.assertEquals(0, len(self.source),
                          'No search performed, length should be 0')

        result = self.source.search('Hans')
        self.assertEquals(len(result), len(self.source),
                          'Length of the source should be equal to the result')

    def test_source__iter__is__iter__of_search_result(self):
        self.assertEquals((), tuple(self.source),
                          'No search performed, no items in source')

        result = self.source.search('Hans')
        self.assertEquals(
            tuple(result), tuple(self.source),
            '__iter__ of the source should be equal to the result')

    def test_all_ogds_users_are_valid(self):
        self.assertIn(u'org-unit-1:john', self.source)
        self.assertIn(u'org-unit-1:hugo', self.source)
        self.assertIn(u'org-unit-1:hans', self.source)
        self.assertIn(u'org-unit-2:hans', self.source)
        self.assertIn(u'org-unit-2:reto', self.source)
        self.assertIn(u'org-unit-2:john', self.source)

        self.assertNotIn(u'dummy:dummy', self.source)
        self.assertNotIn(u'malformed', self.source)
        self.assertNotIn(u'', self.source)

    def test_users_from_inactive_orgunits_are_not_valid(self):
        self.assertNotIn('simon.says', self.source)

    def test_getTerm_can_handle_values_containing_only_a_userid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'org-unit-2')
        source = AllUsersInboxesAndTeamsSource(self.portal)
        self.assertEquals(source.getTerm('hans').token,
                          source.getTerm('org-unit-2:hans').token)

    def test_getTerm_handles_inactive_users(self):
        create(Builder('ogds_user')
               .id('peter.muster')
               .having(firstname='Peter', lastname='Muster', active=False)
               .assign_to_org_units([self.org_unit2]))

        self.assertTrue(self.source.getTerm('org-unit-2:peter.muster'),
                        'Expect a term from inactive user')

    def test_search_for_inactive_users_is_not_possible(self):
        create(Builder('ogds_user')
               .id('peter.muster')
               .having(firstname='Peter', lastname='Muster', active=False)
               .assign_to_org_units([self.org_unit2]))

        self.assertFalse(self.source.search('muster'),
                         'Expect no user, since peter.muster is inactive')

    def test_inboxes_are_in_source_and_in_first_position(self):
        result = self.source.search('Informatik')

        self.assertEquals(4, len(result),
                          'Expect 4 results, 1 Inbox and 3 Users')

        self.assertTermKeys([u'inbox:org-unit-1',
                             u'org-unit-1:hans',
                             u'org-unit-1:hugo',
                             u'org-unit-1:john'],
                            result)

        self.assertEquals('inbox:org-unit-1', result[0].token)
        self.assertEquals(u'Inbox: Informatik', result[0].title)

        self.assertIn('inbox:org-unit-1', self.source)

    def test_do_not_return_inboxes_of_inactive_orgunits(self):
        result = self.source.search('Inbox Steueramt')

        self.assertFalse(result,
                         'Expect no Inbox for the inactive OrgUnit Steueramt')

    def test_do_not_return_inboxes_of_hidden_orgunits(self):
        self.org_unit1.hidden = True
        result = self.source.search('inbox:org-unit-1')

        self.assertFalse(result,
                         'Expect no Inbox for the hidden OrgUnit org-unit-1')

    def test_inboxes_of_hidden_orgunits_are_valid_terms(self):
        self.org_unit1.hidden = True
        term = self.source.getTermByToken('inbox:org-unit-1')

        self.assertTrue(
          term, 'Inbox for the hidden OrgUnit org-unit-1 should be a valid term')
        self.assertEqual('inbox:org-unit-1', term.token)

    def test_search_for_term_inbox_or_partial_term_that_matches_inbox(self):
        inboxes = self.source.search('Inbox')
        self.assertEquals(2, len(inboxes), 'Expect two inboxes')
        self.assertTermKeys(['inbox:org-unit-1', 'inbox:org-unit-2'], inboxes)

        self.assertEquals(2, len(self.source.search('Inb')))
        self.assertEquals(2, len(self.source.search('inbo')))
        self.assertEquals(2, len(self.source.search('box')))
        self.assertEquals(2, len(self.source.search('nbo')))

    def test_only_users_of_the_current_orgunit_and_inboxes_are_valid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'org-unit-1')
        source = self.source = AllUsersInboxesAndTeamsSource(
            self.portal,
            only_current_orgunit=True)

        self.assertIn(u'org-unit-1:john', source)
        self.assertIn(u'org-unit-1:hugo', source)
        self.assertIn(u'org-unit-1:hans', source)

        # Not assigned users are still valid but not returned by search
        self.assertIn(u'org-unit-2:hans', source)
        self.assertIn(u'org-unit-2:reto', source)
        self.assertTermKeys([u'inbox:org-unit-1', u'inbox:org-unit-2', u'org-unit-1:john',
                             u'org-unit-1:hugo', u'org-unit-1:hans'],
                            source.search('unit'))

    def test_only_the_current_inbox_is_valid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'org-unit-1')
        source = self.source = AllUsersInboxesAndTeamsSource(
            self.portal,
            only_current_inbox=True)

        self.assertIn('inbox:org-unit-1', source)
        self.assertNotIn('inbox:org-unit-2', source)

        self.assertTermKeys([u'inbox:org-unit-1'],
                            source.search('Inb'))

    def test_teams_are_only_in_source_when_flag_is_true(self):
        create(Builder('ogds_team')
               .having(title=u'Projekt \xdcberbaung Dorfmatte',
                       group=self.org_unit1.users_group,
                       org_unit=self.org_unit1))
        create(Builder('ogds_team')
               .having(title=u'Projekt IT-Restrukturierung',
                       group=self.org_unit1.users_group,
                       org_unit=self.org_unit1))
        create(Builder('ogds_team')
               .having(title=u'Abteilung Kommunikation',
                       group=self.org_unit1.users_group,
                       org_unit=self.org_unit1))

        source = AllUsersInboxesAndTeamsSource(self.portal)

        self.assertEquals([], source.search('Projekt'))

        source = AllUsersInboxesAndTeamsSource(self.portal, include_teams=True)
        self.assertTermKeys(['team:1', 'team:2'], source.search('Projekt'))

    def test_teams_are_only_valid_when_flag_is_true(self):
        create(Builder('ogds_team')
               .having(title=u'Projekt \xdcberbaung Dorfmatte',
                       group=self.org_unit1.users_group,
                       org_unit=self.org_unit1))

        source = AllUsersInboxesAndTeamsSource(self.portal)
        self.assertNotIn('team:1', source)

        source = AllUsersInboxesAndTeamsSource(self.portal, include_teams=True)
        self.assertIn('team:1', source)
        self.assertNotIn('team:2', source)


class TestUsersContactsInboxesSource(SolrIntegrationTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestUsersContactsInboxesSource, self).setUp()

        self.org_unit, self.admin_unit = create(
            Builder('fixture').with_admin_unit().with_org_unit())

        org_unit_2 = create(Builder('org_unit')
                            .id('org-unit-2')
                            .with_default_groups()
                            .having(title='Org Unit 2',
                                    admin_unit=self.admin_unit))

        disabled_unit = create(Builder('org_unit')
                               .id('org-unit-3')
                               .having(title=u'Steueramt',
                                       enabled=False,
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        create(Builder('ogds_user')
               .having(firstname=u'Test', lastname=u'User')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user')
               .id('hugo.boss')
               .having(firstname=u'Hugo', lastname=u'Boss')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user').id('robin.hood')
               .having(firstname=u'Robin', lastname=u'Hood')
               .assign_to_org_units([org_unit_2]))

        create(Builder('ogds_user').id('simon.says')
               .having(firstname='Simon', lastname='Says')
               .assign_to_org_units([disabled_unit]))

        create(Builder('contact')
               .having(firstname=u'Lara', lastname=u'Croft',
                       email=u'lara.croft@example.com'))
        create(Builder('contact')
               .having(firstname=u'Super', lastname=u'M\xe4n',
                       email='superman@example.com'))

        self.commit_solr()
        self.source = UsersContactsInboxesSource(self.portal)

    def test_all_ogds_users_are_valid(self):
        self.assertIn('test_user_1_', self.source)
        self.assertIn('hugo.boss', self.source)
        self.assertIn('robin.hood', self.source)

    def test_users_from_inactive_orgunits_are_valid_but_not_found_by_search(self):
        self.assertIn('simon.says', self.source)
        self.assertEquals([], self.source.search('simon'))

    def test_return_no_search_result_for_inactive_orgunits(self):
        result = self.source.search('Steueramt')

        self.assertFalse(result,
                         'Expect no result, since the Steueramt is disabled')

    def test_not_existing_users(self):
        self.assertNotIn('dummy.user', self.source)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken('hugo.boss')
        self.assertEquals('hugo.boss', term.token)
        self.assertEquals('hugo.boss', term.value)
        self.assertEquals('Boss Hugo (hugo.boss)', term.title)

    def test_inboxes_are_valid(self):
        self.assertIn('inbox:org-unit-1', self.source)
        self.assertIn('inbox:org-unit-2', self.source)

    def test_contacts_are_valid(self):
        self.assertIn('contact:croft-lara', self.source)
        self.assertIn('contact:man-super', self.source)

    def test_search_contacts(self):
        self.login(self.administrator)

        result = self.source.search('Lara')

        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('contact:croft-lara', result[0].token)
        self.assertEquals('contact:croft-lara', result[0].value)
        self.assertEquals('Croft Lara (lara.croft@example.com)', result[0].title)

    def test_search_ogds_users(self):
        self.assertEquals('hugo.boss', self.source.search('Hugo')[0].token)
        self.assertEquals('robin.hood', self.source.search('Rob')[0].token)


class TestAssignedUsersSource(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestAssignedUsersSource, self).setUp()

        self.admin_unit = create(Builder('admin_unit').as_current_admin_unit())

        user = create(Builder('ogds_user').having(firstname='Test',
                                                  lastname='User'))
        additional = create(Builder('admin_unit')
                            .id('additional')
                            .having(title='additional'))

        self.org_unit = create(Builder('org_unit').id('org-unit-1')
                               .having(title=u"Org Unit 1",
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        org_unit_2 = create(Builder('org_unit').id('org-unit-2')
                            .having(title=u"Org Unit 2",
                                    admin_unit=self.admin_unit)
                            .with_default_groups()
                            .assign_users([user])
                            .as_current_org_unit())

        org_unit_3 = create(Builder('org_unit')
                            .id('org-unit-3')
                            .having(title=u"Org Unit 3", admin_unit=additional)
                            .with_default_groups())

        disabled_unit = create(Builder('org_unit')
                               .id('org-unit-4')
                               .having(title=u'Steueramt',
                                       enabled=False,
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        create(Builder('ogds_user').id('hugo.boss')
               .having(firstname='Test', lastname='User')
               .assign_to_org_units([self.org_unit]))

        create(Builder('ogds_user').id('peter.muster')
               .having(firstname='Peter', lastname='Muster')
               .assign_to_org_units([org_unit_2]))

        create(Builder('ogds_user').id('jamie.lannister')
               .having(firstname='Jamie', lastname='Lannister')
               .assign_to_org_units([self.org_unit, org_unit_2]))

        create(Builder('ogds_user').id('peter.meier')
               .having(firstname='Peter', lastname='Meier')
               .assign_to_org_units([org_unit_3]))

        create(Builder('ogds_user').id('simon.says')
               .having(firstname='Simon', lastname='Says')
               .assign_to_org_units([disabled_unit]))

        self.source = AssignedUsersSource(self.portal)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken(u'hugo.boss')
        self.assertTrue(isinstance(term, SimpleTerm))
        self.assertEquals(u'User Test (hugo.boss)', term.title)

    def test_get_term_by_token_raises_BadReques_if_no_token(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken(None)

    def test_get_term_by_token_raises_LookupError_if_no_result(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('dummy:dummy')

    def test_title_token_and_value_of_term(self):
        result = self.source.search('hugo')
        self.assertEqual(1, len(result), 'Expect one result. only Hugo')
        self.assertEquals(u'hugo.boss', result[0].token)
        self.assertEquals(u'hugo.boss', result[0].value)
        self.assertEquals(u'User Test (hugo.boss)', result[0].title)

    def test_users_of_all_admin_unit_are_valid(self):
        self.assertIn('hugo.boss', self.source)
        self.assertIn('peter.muster', self.source)
        self.assertIn('jamie.lannister', self.source)
        self.assertIn(TEST_USER_ID, self.source)
        # User from other admin_unit is also valid
        self.assertIn('peter.meier', self.source)

    def test_only_users_of_current_admin_unit_are_found_by_search(self):
        results = self.source.search("hugo.boss")
        self.assertEqual(1, len(results))
        self.assertEqual('hugo.boss', results[0].value)

        # User from other admin_unit cannot be found
        results = self.source.search('peter.meier')
        self.assertEqual(0, len(results))

    def test_users_from_inactive_orgunits_are_valid_but_not_found_by_search(self):
        self.assertIn('simon.says', self.source)
        self.assertEquals([], self.source.search('simon'))

    def test_getTerm_handles_inactive_users(self):
        create(Builder('ogds_user')
               .id('john.doe')
               .having(firstname='John', lastname='Doe', active=False)
               .assign_to_org_units([self.org_unit]))

        self.assertTrue(self.source.getTerm('john.doe'),
                        'Expect a term from inactive user')

    def test_search_for_inactive_users_is_not_possible(self):
        create(Builder('ogds_user')
               .id('john.doe')
               .having(firstname='John', lastname='Doe', active=False)
               .assign_to_org_units([self.org_unit]))

        self.assertFalse(self.source.search('Doe'),
                         'Expect no user, since john.doe is inactive')


class TestAllUsersSource(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestAllUsersSource, self).setUp()

        self.admin_unit = create(Builder('admin_unit').as_current_admin_unit())

        user = create(Builder('ogds_user').having(firstname='Test',
                                                  lastname='User'))
        additional = create(Builder('admin_unit')
                            .id('additional')
                            .having(title='additional'))

        self.org_unit = create(Builder('org_unit').id('org-unit-1')
                               .having(title=u"Org Unit 1",
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        org_unit_2 = create(Builder('org_unit').id('org-unit-2')
                            .having(title=u"Org Unit 2",
                                    admin_unit=self.admin_unit)
                            .with_default_groups()
                            .assign_users([user])
                            .as_current_org_unit())

        org_unit_3 = create(Builder('org_unit')
                            .id('org-unit-3')
                            .having(title=u"Org Unit 3", admin_unit=additional)
                            .with_default_groups())

        disabled_unit = create(Builder('org_unit')
                               .id('org-unit-4')
                               .having(title=u'Steueramt',
                                       enabled=False,
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        create(Builder('ogds_user').id('hugo.boss')
               .having(firstname='Test', lastname='User')
               .assign_to_org_units([self.org_unit]))

        create(Builder('ogds_user').id('peter.muster')
               .having(firstname='Peter', lastname='Muster')
               .assign_to_org_units([org_unit_2]))

        create(Builder('ogds_user').id('jamie.lannister')
               .having(firstname='Jamie', lastname='Lannister')
               .assign_to_org_units([self.org_unit, org_unit_2]))

        create(Builder('ogds_user').id('peter.meier')
               .having(firstname='Peter', lastname='Meier')
               .assign_to_org_units([org_unit_3]))

        create(Builder('ogds_user')
               .id('john.doe')
               .having(firstname='John', lastname='Doe', active=False)
               .assign_to_org_units([self.org_unit]))

        create(Builder('ogds_user').id('simon.says')
               .having(firstname='Simon', lastname='Says')
               .assign_to_org_units([disabled_unit]))

        create(Builder('ogds_user').id('without.orgunit')
               .having(firstname='User Without', lastname='Orgunit'))

        self.source = AllUsersSource(self.portal)

    def test_all_users_are_valid(self):
        self.assertIn('hugo.boss', self.source)
        self.assertIn('peter.muster', self.source)
        self.assertIn('jamie.lannister', self.source)
        self.assertIn(TEST_USER_ID, self.source)
        self.assertIn('peter.meier', self.source)
        self.assertIn('john.doe', self.source)
        self.assertIn('without.orgunit', self.source)

    def test_users_from_inactive_orgunits_are_valid_but_not_found_by_search(self):
        self.assertIn('simon.says', self.source)
        self.assertEquals([], self.source.search('simon'))

    def test_users_without_orgunits_are_valid_but_not_found_by_search(self):
        self.assertIn('without.orgunit', self.source)
        self.assertEquals([], self.source.search('without'))

    def test_users_without_orgunits_are_valid_and_found_by_search_if_requested(self):
        source = AllUsersSource(self.portal, only_active_orgunits=False)
        self.assertIn('without.orgunit', source)

        result = source.search('without')
        self.assertEquals(
            1, len(result),
            'Expected user Without Orgunit in result')

        self.assertEquals('without.orgunit', result[0].token)

    def test_users_assigned_to_other_admin_units_are_valid_and_found_by_search(self):
        self.assertIn('peter.meier', self.source)
        result = self.source.search('meier')
        self.assertEquals(
            1, len(result),
            'Expected user Peter Meier from other admin unit in result')

        self.assertEquals('peter.meier', result[0].token)

    def test_return_no_search_result_for_inactive_orgunits(self):
        result = self.source.search('Simon')
        self.assertFalse(result,
                         'Expect no result, since the Steueramt is disabled')

    def test_search_for_inactive_users_is_possible(self):
        result = self.source.search('Doe')
        self.assertEquals(1, len(result),
                          'Expect the inactive user John Doe in result')

        self.assertEquals('john.doe', result[0].token)


class TestAllEmailContactsAndUsersSource(SolrIntegrationTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestAllEmailContactsAndUsersSource, self).setUp()

        self.org_unit, self.admin_unit = create(
            Builder('fixture').with_admin_unit().with_org_unit())

        disabled_unit = create(Builder('org_unit')
                               .id('org-unit-4')
                               .having(title=u'Steueramt',
                                       enabled=False,
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        create(Builder('ogds_user')
               .having(firstname=u'Test', lastname=u'User')
               .having(email='onlyone@example.com')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user')
               .id('hugo.boss')
               .having(firstname=u'Hugo', lastname=u'Boss')
               .having(email='hugos@example.com', email2='huegeler@example.com')
               .assign_to_org_units([self.org_unit]))

        create(Builder('ogds_user').id('simon.says')
               .having(firstname='Simon', lastname='Says')
               .assign_to_org_units([disabled_unit]))

        create(Builder('contact')
               .having(firstname=u'Lara', lastname=u'Croft',
                       email=u'lara.croft@example.com'))
        create(Builder('contact')
               .having(firstname=u'Super', lastname=u'M\xe4n',
                       email='superman@example.com',
                       email2='superman@example.com'))

        self.commit_solr()
        self.source = AllEmailContactsAndUsersSource(self.portal)

    def test_ogds_users_are_valid(self):
        self.assertIn('onlyone@example.com:test_user_1_', self.source)

        self.assertIn('hugos@example.com:hugo.boss', self.source)
        self.assertIn('huegeler@example.com:hugo.boss', self.source)

    def test_users_from_inactive_orgunits_are_not_valid(self):
        self.assertNotIn('simon.says', self.source)

    def test_return_no_search_result_for_inactive_orgunits(self):
        result = self.source.search('Simon')

        self.assertFalse(result,
                         'Expect no result, since the Steueramt is disabled')

    def test_invalid_ogds_tokens(self):
        self.assertNotIn('notthere@example.com:hugo-boss', self.source)
        self.assertNotIn('boss-hugo', self.source)
        self.assertNotIn('hugo:boss', self.source)
        self.assertNotIn('hugo.boss', self.source)
        self.assertNotIn('hugos@example.com', self.source)
        self.assertNotIn('lara@example.com:lara-croft', self.source)

    def test_contacts_are_valid(self):
        self.assertIn('lara.croft@example.com:croft-lara', self.source)

        self.assertIn('superman@example.com:man-super', self.source)
        self.assertIn('superman@example.com:man-super', self.source)

    def test_invalid_contact_tokens(self):
        self.assertNotIn('lara.croft@example.com:lara-croft', self.source)
        self.assertNotIn('man-super:superman@example.com', self.source)
        self.assertNotIn('notthere@example.com:man-super', self.source)

    def test_search_returns_one_entry_for_each_email_address(self):
        self.login(self.administrator)

        ogds_result = self.source.search('Hugo')

        self.assertEquals(
            2, len(ogds_result),
            'Expect 2 results, since the user has 2 email addresses')

        self.assertEquals('hugos@example.com:hugo.boss', ogds_result[0].token)
        self.assertEquals('hugos@example.com:hugo.boss', ogds_result[0].value)
        self.assertEquals('Boss Hugo (hugo.boss, hugos@example.com)',
                          ogds_result[0].title)

        self.assertEquals('huegeler@example.com:hugo.boss', ogds_result[1].token)
        self.assertEquals('huegeler@example.com:hugo.boss', ogds_result[1].value)
        self.assertEquals('Boss Hugo (hugo.boss, huegeler@example.com)',
                          ogds_result[1].title)

        person_result = self.source.search('Super')

        self.assertEquals(
            2, len(person_result),
            'Expect 2 results, since the user has 2 email addresses')

        self.assertEquals('superman@example.com:man-super', person_result[0].token)
        self.assertEquals('superman@example.com:man-super', person_result[0].value)
        self.assertEquals(u'M\xe4n Super (superman@example.com)',
                          person_result[0].title)

        self.assertEquals('superman@example.com:man-super', person_result[1].token)
        self.assertEquals('superman@example.com:man-super', person_result[1].value)
        self.assertEquals(u'M\xe4n Super (superman@example.com)',
                          person_result[1].title)


class TestContactsSource(SolrIntegrationTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestContactsSource, self).setUp()

        self.org_unit, self.admin_unit = create(
            Builder('fixture').with_admin_unit().with_org_unit())

        create(Builder('ogds_user')
               .id('hugo.boss')
               .having(firstname=u'Hugo', lastname=u'Boss')
               .assign_to_org_units([self.org_unit]))
        create(Builder('contact')
               .having(firstname=u'Lara', lastname=u'Croft',
                       email=u'lara.croft@example.com'))
        create(Builder('contact')
               .having(firstname=u'Super', lastname=u'M\xe4n',
                       email='superman@example.com'))

        self.commit_solr()
        self.source = ContactsSource(self.portal)

    def test_ogds_users_are_invalid(self):
        self.assertNotIn('test_user_1_', self.source)

    def test_all_contacts_are_valid(self):
        self.assertIn('contact:croft-lara', self.source)
        self.assertIn('contact:man-super', self.source)

    def test_not_existing_contact_is_invalid(self):
        self.assertNotIn('contact:not-existing', self.source)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken('contact:man-super')
        self.assertEquals('contact:man-super', term.token)
        self.assertEquals('contact:man-super', term.value)
        self.assertEquals(u'M\xe4n Super (superman@example.com)', term.title)

    def test_search_contacts(self):
        self.login(self.administrator)

        result = self.source.search('Lara')

        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('contact:croft-lara', result[0].token)
        self.assertEquals('contact:croft-lara', result[0].value)
        self.assertEquals('Croft Lara (lara.croft@example.com)', result[0].title)

    def test_search_ogds_users_is_empty(self):
        self.assertEquals([], self.source.search('Hugo'))


class TestCurrentAdminUnitOrgUnitsSource(IntegrationTestCase):

    def setUp(self):
        super(TestCurrentAdminUnitOrgUnitsSource, self).setUp()
        self.source = CurrentAdminUnitOrgUnitsSource(self.portal)

        create(Builder('org_unit')
               .id('afi')
               .having(title=u'Amt f\xfcr Informatik',
                       admin_unit_id='plone',
                       enabled=False))

        self.additional = create(Builder('admin_unit')
                                 .id('additional'))
        self.org_unit = create(Builder('org_unit')
                               .id('ska')
                               .having(title=u'Staatskanzlei',
                                       admin_unit=self.additional,
                                       enabled=True)
                               .with_default_groups())

    def test_all_org_unit_ids_are_valid(self):
        self.assertIn('fa', self.source)
        self.assertIn('afi', self.source)
        self.assertIn('ska', self.source)

    def test_not_existing_org_unit_ids(self):
        self.assertNotIn('not', self.source)

    def test_search_finds_only_enabled_org_units(self):
        result = self.source.search('Finanz')

        self.assertEqual(1, len(result), 'Expect one result. only Finanzamt')
        self.assertEqual('fa', result[0].token)
        self.assertEqual('fa', result[0].value)
        self.assertEqual(u'Finanz\xe4mt', result[0].title)

        result = self.source.search('Informatik')
        self.assertEqual(0, len(result),
                         'Expect zero results. The afi orgunit is disabled.')

    def test_invalid_token_raises_lookup_error(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('invalid-id')

    def test_do_not_find_org_units_of_other_admin_units(self):
        self.assertEqual(1, len(self.source.search(u'Finanz\xe4mt')))
        self.assertEqual(0, len(self.source.search('Staatskanzlei')))

        api.portal.set_registry_record('current_unit_id',
                                       self.additional.id().decode('utf-8'),
                                       IAdminUnitConfiguration)

        self.assertEqual(0, len(self.source.search('Finanzamt')))
        self.assertEqual(1, len(self.source.search('Staatskanzlei')))


class TestAllGroupsSource(IntegrationTestCase):

    def setUp(self):
        super(TestAllGroupsSource, self).setUp()
        self.source = AllGroupsSource(self.portal)

    def test_all_group_ids_are_valid(self):
        self.assertIn('fa_users', self.source)
        self.assertIn('fa_inbox_users', self.source)

        group = Group.query.get('projekt_a')
        group.active = False

        self.assertIn('projekt_a', self.source)

    def test_not_existing_org_unit_ids(self):
        self.assertNotIn('not', self.source)

    def test_search_finds_only_enabled_org_units(self):
        result = self.source.search('projek')
        self.assertEqual(3, len(result), 'Expected three results.')
        self.assertEquals(['projekt_a', 'projekt_b', 'projekt_laeaer'], [item.value for item in result])
        self.assertEquals(['Projekt A', 'Projekt B', u'Projekt L\xc3\xa4\xc3\xa4r'], [item.title for item in result])

        group = Group.query.get('projekt_b')
        group.active = False
        result = self.source.search('projek')
        self.assertEqual(2, len(result), 'Expected two results.')

    def test_invalid_token_raises_lookup_error(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('invalid-id')


class TestAllUsersAndGroupsSource(IntegrationTestCase):

    def setUp(self):
        super(TestAllUsersAndGroupsSource, self).setUp()
        self.source = AllUsersAndGroupsSource(self.portal)

    def get_groups(self):
        return [term.value for term in self.source.search('') if term.token.startswith('group:')]

    def test_find_users(self):
        self.assertIn('kathi.barfuss', self.source)
        self.assertIn('herbert.jager', self.source)

    def test_find_groups_with_prefix(self):
        self.assertIn('group:fa_users', self.source)
        self.assertIn('group:fa_inbox_users', self.source)

    def test_find_groups_without_prefix(self):
        self.assertIn('fa_users', self.source)
        self.assertIn('fa_inbox_users', self.source)

    def test_term_token_always_includes_prefix(self):
        self.assertEqual('group:fa_users',
                         self.source.getTermByToken('fa_users').token)
        self.assertEqual('group:fa_users',
                         self.source.getTermByToken('group:fa_users').token)

    def test_term_value_never_includes_prefix(self):
        self.assertEqual('fa_users',
                         self.source.getTermByToken('fa_users').value)
        self.assertEqual('fa_users',
                         self.source.getTermByToken('fa_users').value)

    def test_search_does_not_find_blacklisted_groups(self):
        expected_groups = [
            u'fa_users',
            u'fa_inbox_users',
            u'rk_users',
            u'rk_inbox_users',
            u'projekt_a',
            u'projekt_b',
            u'projekt_laeaer',
            u'committee_rpk_group',
            u'committee_ver_group',
        ]
        self.assertListEqual(expected_groups, self.get_groups())

        # Whitelist no group explicitly.
        api.portal.set_registry_record('white_list_prefix', u'^$', ISharingConfiguration)

        # Blacklist all groups beginning with `fa_`.
        api.portal.set_registry_record('black_list_prefix', u'^fa_', ISharingConfiguration)

        expected_groups = [
            u'rk_users',
            u'rk_inbox_users',
            u'projekt_a',
            u'projekt_b',
            u'projekt_laeaer',
            u'committee_rpk_group',
            u'committee_ver_group',
        ]
        self.assertListEqual(expected_groups, self.get_groups())

        # Blacklist all groups
        api.portal.set_registry_record('black_list_prefix', u'^.', ISharingConfiguration)
        self.assertEqual([], self.get_groups())

    def test_search_finds_whitelisted_org_groups(self):
        # Blacklist all groups.
        api.portal.set_registry_record(
            'black_list_prefix', u'^.', ISharingConfiguration
        )

        # Whitelist all groups beginning with `fa_` explicitly.
        api.portal.set_registry_record(
            'white_list_prefix', u'^fa_', ISharingConfiguration
        )
        expected_principals = [
            u'fa_users',
            u'fa_inbox_users',
        ]
        self.assertEqual(expected_principals, self.get_groups())


class TestAllFilteredGroupsSource(TestAllGroupsSource):

    def setUp(self):
        super(TestAllFilteredGroupsSource, self).setUp()
        self.source = AllFilteredGroupsSource(self.portal)

    def test_search_does_not_find_blacklisted_groups(self):
        expected_groups = [
            u'fa_users',
            u'fa_inbox_users',
            u'rk_users',
            u'rk_inbox_users',
            u'projekt_a',
            u'projekt_b',
            u'projekt_laeaer',
            u'committee_rpk_group',
            u'committee_ver_group',
        ]
        self.assertEqual(expected_groups, [term.value for term in self.source.search('')])

        # Whitelist no group explicitly
        api.portal.set_registry_record('white_list_prefix', u'^$', ISharingConfiguration)

        # Blacklist all groups beginning with `fa_`
        api.portal.set_registry_record('black_list_prefix', u'^fa_', ISharingConfiguration)

        expected_groups = [
            u'rk_users',
            u'rk_inbox_users',
            u'projekt_a',
            u'projekt_b',
            u'projekt_laeaer',
            u'committee_rpk_group',
            u'committee_ver_group',
        ]
        self.assertEqual(expected_groups, [term.value for term in self.source.search('')])

        # Blacklist all groups
        api.portal.set_registry_record('black_list_prefix', u'^.', ISharingConfiguration)
        self.assertEqual([], [term.value for term in self.source.search('')])

    def test_search_finds_whitelisted_org_groups(self):
        # Blacklist all groups
        api.portal.set_registry_record('black_list_prefix',
                                       u'^.',
                                       ISharingConfiguration)

        # Whitelist all groups beginning with `fa_` explicitly
        api.portal.set_registry_record('white_list_prefix',
                                       u'^fa_',
                                       ISharingConfiguration)

        self.assertEqual(
            [u'fa_users', u'fa_inbox_users'],
            [term.value for term in self.source.search('')])
