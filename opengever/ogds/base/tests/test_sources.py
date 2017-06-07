from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.sources import AllUsersAndInboxesSource
from opengever.ogds.base.sources import AllUsersSource
from opengever.ogds.base.sources import AssignedUsersSource
from opengever.ogds.base.sources import ForwardingResponsibleSource
from opengever.ogds.base.sources import UsersContactsInboxesSource
from opengever.ogds.base.sources import AllEmailContactsAndUsersSource
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.schema.vocabulary import SimpleTerm


class TestAllUsersAndInboxesSource(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestAllUsersAndInboxesSource, self).setUp()

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
                                                 self.org_unit2]))
        self.reto = create(Builder('ogds_user')
                           .id('reto')
                           .having(firstname=u'Reto', lastname=u'Rageto')
                           .assign_to_org_units([self.org_unit2]))

        self.source = AllUsersAndInboxesSource(self.portal)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken(u'unit1:hans')
        self.assertTrue(isinstance(term, SimpleTerm))
        self.assertEquals(u'Informatik: Peter Hans (test@example.org)',
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
        self.assertEquals(u'Informatik: Doe John (test@example.org)',
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

    def test_user_is_once_per_orgunit_in_resultset(self):
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

        self.assertNotIn(u'dummy:dummy', self.source)
        self.assertNotIn(u'malformed', self.source)
        self.assertNotIn(u'unit2:john', self.source)
        self.assertNotIn(u'', self.source)

    def test_getTerm_can_handle_values_containing_only_a_userid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit2')
        source = AllUsersAndInboxesSource(self.portal)
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
        source = self.source = AllUsersAndInboxesSource(
            self.portal,
            only_current_orgunit=True)

        self.assertIn(u'unit1:john', source)
        self.assertIn(u'unit1:hugo', source)
        self.assertIn(u'unit1:hans', source)
        self.assertNotIn(u'unit2:hans', source)
        self.assertNotIn(u'unit2:reto', source)

        self.assertTermKeys([u'inbox:unit1', u'inbox:unit2', u'unit1:john',
                            u'unit1:hugo', u'unit1:hans'],
                            source.search('unit'))

    def test_only_the_current_inbox_is_valid(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit1')
        source = self.source = AllUsersAndInboxesSource(
            self.portal,
            only_current_inbox=True)

        self.assertIn('inbox:unit1', source)
        self.assertNotIn('inbox:unit2', source)

        self.assertTermKeys([u'inbox:unit1'],
                            source.search('Inb'))


class TestForwardingResponsibleSource(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestForwardingResponsibleSource, self).setUp()

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

        self.hugo = create(Builder('ogds_user')
                           .id('hugo')
                           .having(firstname=u'Hugo', lastname=u'Boss')
                           .assign_to_org_units([self.org_unit1]))
        self.hans = create(Builder('ogds_user')
                           .id('hans')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .assign_to_org_units([self.org_unit1,
                                                 self.org_unit2]))

    def test_search_returns_only_users_of_the_given_client(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit1')
        source = ForwardingResponsibleSource(self.portal)
        self.assertTermKeys(['unit1:hans'], source.search('hans'))

    def test_search_all_inboxes(self):
        self.portal.REQUEST.set('form.widgets.responsible_client', 'unit1')
        source = ForwardingResponsibleSource(self.portal)
        self.assertTermKeys(['inbox:unit1', 'inbox:unit2'],
                            source.search('Inb'))


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

    def test_not_existing_users(self):
        self.assertNotIn('dummy.user', self.source)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken('hugo.boss')
        self.assertEquals('hugo.boss', term.token)
        self.assertEquals('hugo.boss', term.value)
        self.assertEquals('Boss Hugo (test@example.org)', term.title)

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

        self.source = AssignedUsersSource(self.portal)

    def test_get_term_by_token(self):
        term = self.source.getTermByToken(u'hugo.boss')
        self.assertTrue(isinstance(term, SimpleTerm))
        self.assertEquals(u'User Test (test@example.org)', term.title)

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
        self.assertEquals(u'User Test (test@example.org)', result[0].title)

    def test_only_users_of_the_current_admin_unit_are_valid(self):

        self.assertIn('hugo.boss', self.source)
        self.assertIn('peter.muster', self.source)
        self.assertIn('jamie.lannister', self.source)
        self.assertIn(TEST_USER_ID, self.source)

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

        self.source = AllUsersSource(self.portal)

    def test_all_users_are_valid(self):

        self.assertIn('hugo.boss', self.source)
        self.assertIn('peter.muster', self.source)
        self.assertIn('jamie.lannister', self.source)
        self.assertIn(TEST_USER_ID, self.source)
        self.assertIn('peter.meier', self.source)
        self.assertIn('john.doe', self.source)

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

        create(Builder('ogds_user')
               .having(firstname=u'Test', lastname=u'User')
               .having(email='onlyone@mail.com')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user')
               .id('hugo.boss')
               .having(firstname=u'Hugo', lastname=u'Boss')
               .having(email='hugos@mail.com', email2='huegeler@mail.com')
               .assign_to_org_units([self.org_unit]))

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
