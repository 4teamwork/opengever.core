from opengever.ogds.models.user import User
from sqlalchemy.orm.exc import NoResultFound
from opengever.ogds.models.tests.base import OGDSTestCase


class TestQueryBase(OGDSTestCase):
    def test_count(self):
        self.assertEqual(6, User.count())

    def test_get_by(self):
        self.assertEqual(self.john, User.get_by(userid='john'))
        self.assertIsNone(User.get_by(firstname='blabla'))

    def test_get_one(self):
        self.assertEqual(self.hugo, User.get_one(userid='hugo'))
        with self.assertRaises(NoResultFound):
            User.get_one(userid='asd')

    def test_get(self):
        self.assertEqual(self.john, User.get('john'))
        self.assertIsNone(User.get('asds'))


class TestUserQuery(OGDSTestCase):
    def test_by_searchable_text(self):
        self.assertEqual([self.hugo], User.query.by_searchable_text(['hu']).all())
        self.assertEqual([self.peter], User.query.by_searchable_text(['pet']).all())
        self.assertEqual([self.john, self.jack], User.query.by_searchable_text(['Sm']).all())

    def test_by_searchable_text_is_case_insensitive(self):
        self.assertEqual([self.peter], User.query.by_searchable_text(['peter']).all())

    def test_by_searchable_handles_multiple_text_snippets(self):
        self.assertEqual([self.john, self.jack], User.query.by_searchable_text(['Sm', 'example']).all())
        self.assertEqual([self.john], User.query.by_searchable_text(['Sm', 'Jo']).all())

    def test_handles_no_ascii_characters_correctly(self):
        self.assertEqual([self.peter], User.query.by_searchable_text([u'Zw\xf6i']).all())

    def test_handles_asterisk_correctly(self):
        self.assertEqual([self.john, self.jack], User.query.by_searchable_text([u'sm*', 'exam*ple']).all())
        self.assertEqual([self.john, self.jack], User.query.by_searchable_text([u'sm*']).all())
        self.assertEqual([self.john, self.jack], User.query.by_searchable_text([u'*ith']).all())

    def test_by_searchable_text_ignores_empty_list(self):
        expected_users = [self.john, self.hugo, self.peter, self.jack, self.bob, self.admin]
        self.assertEqual(expected_users, User.query.by_searchable_text([]).all())

    def test_by_searchable_text_ignores_none_text(self):
        expected_users = [self.john, self.hugo, self.peter, self.jack, self.bob, self.admin]
        self.assertEqual(expected_users, User.query.by_searchable_text(None).all())
