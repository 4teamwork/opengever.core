from opengever.ogds.models.testing import DATABASE_LAYER
from opengever.ogds.models.user import User
from sqlalchemy.orm.exc import NoResultFound
import unittest2


class TestQueryBase(unittest2.TestCase):

    layer = DATABASE_LAYER

    @property
    def session(self):
        return self.layer.session

    def setUp(self):
        super(TestQueryBase, self).setUp()
        self.john = User('john')
        self.hugo = User('hugo')
        self.session.add(self.john)
        self.session.add(self.hugo)

    def test_count(self):
        self.assertEqual(2, User.count())

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


class TestUserQuery(unittest2.TestCase):

    layer = DATABASE_LAYER

    @property
    def session(self):
        return self.layer.session

    def setUp(self):
        super(TestUserQuery, self).setUp()
        self.jason = User('jj', firstname="Jason", lastname='Brown',
                          email='jason.brow@example.org')
        self.hugo = User('hb', firstname="Hugo", lastname='Bred',
                         email='hugo.bred@example.org')
        self.james = User('007', firstname="James", lastname='Bond',
                          email=u'b\xf6nd@example.org')

        self.session.add(self.jason)
        self.session.add(self.hugo)
        self.session.add(self.james)

    def test_by_searchable_text(self):
        self.assertEqual(
            [self.hugo,],
            User.query.by_searchable_text(['hu', ]).all())

        self.assertEqual(
            [self.jason,],
            User.query.by_searchable_text(['bro']).all())

        self.assertEqual(
            [self.jason, self.hugo],
            User.query.by_searchable_text(['Br']).all())

    def test_by_searchable_text_is_case_insensitive(self):
        self.assertEqual(
            [self.james],
            User.query.by_searchable_text(['james']).all())

    def test_by_searchable_handles_multiple_text_snippets(self):
        self.assertEqual(
            [self.jason, self.hugo],
            User.query.by_searchable_text(['Br', 'example']).all())

        self.assertEqual(
            [self.hugo],
            User.query.by_searchable_text(['Br', 'go']).all())

    def test_handles_no_ascii_characters_correctly(self):
        self.assertEqual(
            [self.james],
            User.query.by_searchable_text([u'b\xf6nd']).all())

    def test_handles_asterisk_correctly(self):
        self.assertEqual(
            [self.jason, self.hugo],
            User.query.by_searchable_text([u'br*', 'exam*ple']).all())
        self.assertEqual(
            [self.jason, self.hugo],
            User.query.by_searchable_text([u'br*']).all())
        self.assertEqual(
            [self.jason, self.hugo],
            User.query.by_searchable_text([u'*br']).all())

    def test_by_searchable_text_ignores_empty_list(self):
        self.assertEqual(
            [self.jason, self.hugo, self.james],
            User.query.by_searchable_text([]).all())

    def test_by_searchable_text_ignores_none_text(self):
        self.assertEqual(
            [self.jason, self.hugo, self.james],
            User.query.by_searchable_text(None).all())
