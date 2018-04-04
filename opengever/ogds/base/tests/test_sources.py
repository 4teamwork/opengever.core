from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.sources import AllEmailContactsAndUsersSource
from opengever.ogds.base.sources import AllGroupsSource
from opengever.ogds.base.sources import AllOrgUnitsSource
from opengever.ogds.base.sources import AllUsersAndGroupsSource
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.ogds.base.sources import AllUsersSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import ContactsSource
from opengever.ogds.base.sources import UsersContactsInboxesSource
from opengever.ogds.models.group import Group
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from zope.schema.vocabulary import SimpleTerm


class TestAllUsersInboxesAndTeamsSource(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestAllUsersInboxesAndTeamsSource, self).setUp()

        self.admin_unit = create(Builder('admin_unit'))
        self.org_unit1 = create(Builder('org_unit')
                                .id('unit1')
                                .having(title=u'Informatik',
                                        admin_unit=self.admin_unit)
                                .with_default_groups())
        self.org_unit2 = create(Builder('org_unit')
                                .id('unit2')
                                .having(title=u'Finanzdirektion',
                                        admin_unit=self.admin_unit)
                                .with_default_groups())

        self.disabled_unit = create(Builder('org_unit')
                                    .id('unit3')
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
        term = self.source.getTermByToken(u'unit1:hans')
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
        self.assertEquals(u'unit1:john', result[0].token)
        self.assertEquals(u'unit1:john', result[0].value)
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
            ['inbox:unit1', 'unit1:user2', 'unit1:user1', 'unit1:hugo',
             'unit1:john', 'unit1:hans', 'unit1:user3'],
            [term.token for term in self.source.search('Informatik')])

    def test_search_for_orgunit(self):
        result = self.source.search('Informatik')
        result.pop(0)  # Remove inbox

        self.assertEquals(3, len(result), 'Expect 3 items')
        self.assertTermKeys([u'unit1:hans', u'unit1:hugo', u'unit1:john'],
                            result)

    def test_return_no_search_result_for_inactive_orgunits(self):
        result = self.source.search('Steueramt')

        self.assertFalse(result,
                         'Expect no result, since the Steueramt is disabled')

    def test_user_is_once_per_active_orgunit_in_resultset(self):
        result = self.source.search('Hans')

        self.assertEquals(2, len(result), 'Expect 3 items')
        self.assertTermKeys([u'unit1:hans', u'unit2:hans'], result)

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
        self.assertIn(u'unit1:john', self.source)
        self.assertIn(u'unit1:hugo', self.source)
        self.assertIn(u'unit1:hans', self.source)
        self.assertIn(u'unit2:hans', self.source)
        self.assertIn(u'unit2:reto', self.source)
        self.assertIn(u'unit2:john', self.source)

        self.assertNotIn(u'dummy:dummy', self.source)
        self.assertNotIn(u'malformed', self.source)
        self.assertNotIn(u'', self.source)

    def test_users_from_inactive_orgunits_are_not_valid(self):
        self.assertNotIn('simon.says', self.source)

    def test_getTerm_can_handle_values_containing_only_a_userid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit2')
        source = AllUsersInboxesAndTeamsSource(self.portal)
        self.assertEquals(source.getTerm('hans').token,
                          source.getTerm('unit2:hans').token)

    def test_getTerm_handles_inactive_users(self):
        create(Builder('ogds_user')
               .id('peter.muster')
               .having(firstname='Peter', lastname='Muster', active=False)
               .assign_to_org_units([self.org_unit2]))

        self.assertTrue(self.source.getTerm('unit2:peter.muster'),
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

        self.assertTermKeys([u'inbox:unit1',
                             u'unit1:hans',
                             u'unit1:hugo',
                             u'unit1:john'],
                            result)

        self.assertEquals('inbox:unit1', result[0].token)
        self.assertEquals(u'Inbox: Informatik', result[0].title)

        self.assertIn('inbox:unit1', self.source)

    def test_do_not_return_inboxes_of_inactive_orgunits(self):
        result = self.source.search('Inbox Steueramt')

        self.assertFalse(result,
                         'Expect no Inbox for the inactive OrgUnit Steueramt')

    def test_search_for_term_inbox_or_partial_term_that_matches_inbox(self):
        inboxes = self.source.search('Inbox')
        self.assertEquals(2, len(inboxes), 'Expect two inboxes')
        self.assertTermKeys(['inbox:unit1', 'inbox:unit2'], inboxes)

        self.assertEquals(2, len(self.source.search('Inb')))
        self.assertEquals(2, len(self.source.search('inbo')))
        self.assertEquals(2, len(self.source.search('box')))
        self.assertEquals(2, len(self.source.search('nbo')))

    def test_only_users_of_the_current_orgunit_and_inboxes_are_valid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit1')
        source = self.source = AllUsersInboxesAndTeamsSource(
            self.portal,
            only_current_orgunit=True)

        self.assertIn(u'unit1:john', source)
        self.assertIn(u'unit1:hugo', source)
        self.assertIn(u'unit1:hans', source)

        # Not assigned users are still valid but not returned by search
        self.assertIn(u'unit2:hans', source)
        self.assertIn(u'unit2:reto', source)
        self.assertTermKeys([u'inbox:unit1', u'inbox:unit2', u'unit1:john',
                             u'unit1:hugo', u'unit1:hans'],
                            source.search('unit'))

    def test_only_the_current_inbox_is_valid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit1')
        source = self.source = AllUsersInboxesAndTeamsSource(
            self.portal,
            only_current_inbox=True)

        self.assertIn('inbox:unit1', source)
        self.assertNotIn('inbox:unit2', source)

        self.assertTermKeys([u'inbox:unit1'],
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


class TestUsersContactsInboxesSource(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestUsersContactsInboxesSource, self).setUp()

        self.org_unit, self.admin_unit = create(
            Builder('fixture').with_admin_unit().with_org_unit())

        org_unit_2 = create(Builder('org_unit')
                            .id('client2')
                            .with_default_groups()
                            .having(title='Client2',
                                    admin_unit=self.admin_unit))

        disabled_unit = create(Builder('org_unit')
                               .id('client3')
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
                       email=u'lara.croft@test.ch'))
        create(Builder('contact')
               .having(firstname=u'Super', lastname=u'M\xe4n',
                       email='superman@test.ch'))

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
        self.assertIn('inbox:client1', self.source)
        self.assertIn('inbox:client2', self.source)

    def test_contacts_are_valid(self):
        self.assertIn('contact:croft-lara', self.source)
        self.assertIn('contact:man-super', self.source)

    def test_search_contacts(self):
        result = self.source.search('Lara')

        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('contact:croft-lara', result[0].token)
        self.assertEquals('contact:croft-lara', result[0].value)
        self.assertEquals('Croft Lara (lara.croft@test.ch)', result[0].title)

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

        self.org_unit = create(Builder('org_unit').id('client1')
                               .having(title=u"Client 1",
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        org_unit_2 = create(Builder('org_unit').id('client2')
                            .having(title=u"Client 2",
                                    admin_unit=self.admin_unit)
                            .with_default_groups()
                            .assign_users([user])
                            .as_current_org_unit())

        org_unit_3 = create(Builder('org_unit')
                            .id('client3')
                            .having(title=u"Client 3", admin_unit=additional)
                            .with_default_groups())

        disabled_unit = create(Builder('org_unit')
                               .id('client4')
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

    def test_only_users_of_the_current_admin_unit_are_valid(self):

        self.assertIn('hugo.boss', self.source)
        self.assertIn('peter.muster', self.source)
        self.assertIn('jamie.lannister', self.source)
        self.assertIn(TEST_USER_ID, self.source)

    def test_users_from_inactive_orgunits_are_not_valid_but_not_found_by_search(self):
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
                         'Expect no user, since peter.muster is inactive')


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

        self.org_unit = create(Builder('org_unit').id('client1')
                               .having(title=u"Client 1",
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        org_unit_2 = create(Builder('org_unit').id('client2')
                            .having(title=u"Client 2",
                                    admin_unit=self.admin_unit)
                            .with_default_groups()
                            .assign_users([user])
                            .as_current_org_unit())

        org_unit_3 = create(Builder('org_unit')
                            .id('client3')
                            .having(title=u"Client 3", admin_unit=additional)
                            .with_default_groups())

        disabled_unit = create(Builder('org_unit')
                               .id('client4')
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


class TestAllEmailContactsAndUsersSource(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestAllEmailContactsAndUsersSource, self).setUp()

        self.org_unit, self.admin_unit = create(
            Builder('fixture').with_admin_unit().with_org_unit())

        disabled_unit = create(Builder('org_unit')
                               .id('unit4')
                               .having(title=u'Steueramt',
                                       enabled=False,
                                       admin_unit=self.admin_unit)
                               .with_default_groups())

        create(Builder('ogds_user')
               .having(firstname=u'Test', lastname=u'User')
               .having(email='onlyone@mail.com')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user')
               .id('hugo.boss')
               .having(firstname=u'Hugo', lastname=u'Boss')
               .having(email='hugos@mail.com', email2='huegeler@mail.com')
               .assign_to_org_units([self.org_unit]))

        create(Builder('ogds_user').id('simon.says')
               .having(firstname='Simon', lastname='Says')
               .assign_to_org_units([disabled_unit]))

        create(Builder('contact')
               .having(firstname=u'Lara', lastname=u'Croft',
                       email=u'lara.croft@test.ch'))
        create(Builder('contact')
               .having(firstname=u'Super', lastname=u'M\xe4n',
                       email='superman@test.ch',
                       email2='superman@dc.com'))

        self.source = AllEmailContactsAndUsersSource(self.portal)

    def test_ogds_users_are_valid(self):
        self.assertIn('onlyone@mail.com:test_user_1_', self.source)

        self.assertIn('hugos@mail.com:hugo.boss', self.source)
        self.assertIn('huegeler@mail.com:hugo.boss', self.source)

    def test_users_from_inactive_orgunits_are_not_valid(self):
        self.assertNotIn('simon.says', self.source)

    def test_return_no_search_result_for_inactive_orgunits(self):
        result = self.source.search('Simon')

        self.assertFalse(result,
                         'Expect no result, since the Steueramt is disabled')

    def test_invalid_ogds_tokens(self):
        self.assertNotIn('notthere@mail.com:hugo-boss', self.source)
        self.assertNotIn('boss-hugo', self.source)
        self.assertNotIn('hugo:boss', self.source)
        self.assertNotIn('hugo.boss', self.source)
        self.assertNotIn('hugos@mail.com', self.source)
        self.assertNotIn('lara@mail.com:lara-croft', self.source)

    def test_contacts_are_valid(self):
        self.assertIn('lara.croft@test.ch:croft-lara', self.source)

        self.assertIn('superman@test.ch:man-super', self.source)
        self.assertIn('superman@dc.com:man-super', self.source)

    def test_invalid_contact_tokens(self):
        self.assertNotIn('lara.croft@test.ch:lara-croft', self.source)
        self.assertNotIn('man-super:superman@test.ch', self.source)
        self.assertNotIn('notthere@dc.com:man-super', self.source)

    def test_search_returns_one_entry_for_each_email_address(self):
        ogds_result = self.source.search('Hugo')

        self.assertEquals(
            2, len(ogds_result),
            'Expect 2 results, since the user has 2 email addresses')

        self.assertEquals('hugos@mail.com:hugo.boss', ogds_result[0].token)
        self.assertEquals('hugos@mail.com:hugo.boss', ogds_result[0].value)
        self.assertEquals('Boss Hugo (hugo.boss, hugos@mail.com)',
                          ogds_result[0].title)

        self.assertEquals('huegeler@mail.com:hugo.boss', ogds_result[1].token)
        self.assertEquals('huegeler@mail.com:hugo.boss', ogds_result[1].value)
        self.assertEquals('Boss Hugo (hugo.boss, huegeler@mail.com)',
                          ogds_result[1].title)

        person_result = self.source.search('Super')

        self.assertEquals(
            2, len(person_result),
            'Expect 2 results, since the user has 2 email addresses')

        self.assertEquals('superman@test.ch:man-super', person_result[0].token)
        self.assertEquals('superman@test.ch:man-super', person_result[0].value)
        self.assertEquals(u'M\xe4n Super (superman@test.ch)',
                          person_result[0].title)

        self.assertEquals('superman@dc.com:man-super', person_result[1].token)
        self.assertEquals('superman@dc.com:man-super', person_result[1].value)
        self.assertEquals(u'M\xe4n Super (superman@dc.com)',
                          person_result[1].title)


class TestContactsSource(FunctionalTestCase):

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
                       email=u'lara.croft@test.ch'))
        create(Builder('contact')
               .having(firstname=u'Super', lastname=u'M\xe4n',
                       email='superman@test.ch'))

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
        self.assertEquals(u'M\xe4n Super (superman@test.ch)', term.title)

    def test_search_contacts(self):
        result = self.source.search('Lara')

        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('contact:croft-lara', result[0].token)
        self.assertEquals('contact:croft-lara', result[0].value)
        self.assertEquals('Croft Lara (lara.croft@test.ch)', result[0].title)

    def test_search_ogds_users_is_empty(self):
        self.assertEquals([], self.source.search('Hugo'))


class TestAllOrgUnitsSource(IntegrationTestCase):

    def setUp(self):
        super(TestAllOrgUnitsSource, self).setUp()
        self.source = AllOrgUnitsSource(self.portal)
        create(Builder('org_unit')
               .id('afi')
               .having(title=u'Amt f\xfcr Informatik',
                       admin_unit_id='plone',
                       enabled=False))

    def test_all_org_unit_ids_are_valid(self):
        self.assertIn('fa', self.source)
        self.assertIn('afi', self.source)

    def test_not_existing_org_unit_ids(self):
        self.assertNotIn('not', self.source)

    def test_search_finds_only_enabled_org_units(self):
        result = self.source.search('Finanz')

        self.assertEqual(1, len(result), 'Expect one result. only Finanzamt')
        self.assertEquals('fa', result[0].token)
        self.assertEquals('fa', result[0].value)
        self.assertEquals(u'Finanzamt', result[0].title)

        result = self.source.search('Informatik')
        self.assertEqual(0, len(result),
                         'Expect zero results. The afi orgunit is disabled.')

    def test_invalid_token_raises_lookup_error(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('invalid-id')


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

        self.assertEqual(2, len(result), 'Expect two result. Projey A and Projekt B')
        self.assertEquals(['projekt_a', 'projekt_b'],
                          [item.value for item in result])
        self.assertEquals(['Projekt A', 'Projekt B'],
                          [item.title for item in result])

        group = Group.query.get('projekt_b')
        group.active = False

        result = self.source.search('projek')

        self.assertEqual(
            1, len(result),
            'Expect one result, Projekt A - Projekt B is disabled')

    def test_invalid_token_raises_lookup_error(self):
        with self.assertRaises(LookupError):
            self.source.getTermByToken('invalid-id')


class TestAllUsersAndGroupsSource(IntegrationTestCase):

    def setUp(self):
        super(TestAllUsersAndGroupsSource, self).setUp()
        self.source = AllUsersAndGroupsSource(self.portal)

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
