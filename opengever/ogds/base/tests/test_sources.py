from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.sources import AllUsersAndInboxesSource
from opengever.testing import FunctionalTestCase
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

    def test_get_term_by_token_raises_BadReques_if_no_token(self):
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

    def test_search_for_orgunit(self):
        result = self.source.search('Informatik')

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

