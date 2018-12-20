from ftw.builder import Builder
from ftw.builder import create
from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.testing import FunctionalTestCase
from opengever.usermigration.dictstorage import DictstorageMigrator
from opengever.usermigration.exceptions import UserMigrationException


class TestDictstorageMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestDictstorageMigrator, self).setUp()
        self.portal = self.layer['portal']
        self.session = create_session()

        self.old_user = create(Builder('ogds_user').id('old.user'))
        self.new_user = create(Builder('ogds_user').id('new.user'))

        self.old_user_with_dash = create(Builder('ogds_user').id('old-user'))
        self.new_user_with_dash = create(Builder('ogds_user').id('new-user'))

        self.session.add(self.old_user)
        self.session.add(self.new_user)
        self.session.add(self.old_user_with_dash)
        self.session.add(self.new_user_with_dash)

    def test_keys_get_migrated(self):
        entry = DictStorageModel(
            key='ftw.tabbedview-foo-tabbedview_view-bar-old.user',
            value='{}')
        self.session.add(entry)

        migrator = DictstorageMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()

        self.assertEquals('ftw.tabbedview-foo-tabbedview_view-bar-new.user',
                          entry.key)

    def test_keys_get_migrated_for_users_with_dash_in_username(self):
        entry = DictStorageModel(
            key='ftw.tabbedview-foo-tabbedview_view-bar-old-user',
            value='{}')
        self.session.add(entry)

        migrator = DictstorageMigrator(
            self.portal, {'old-user': 'new-user'}, 'move')
        migrator.migrate()

        self.assertEquals('ftw.tabbedview-foo-tabbedview_view-bar-new-user',
                          entry.key)

    def test_raises_if_strict_and_user_doesnt_exist(self):
        entry = DictStorageModel(key='foo-old.user', value='{}')
        self.session.add(entry)
        migrator = DictstorageMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move')

        with self.assertRaises(UserMigrationException):
            migrator.migrate()

    def test_doesnt_raise_if_not_strict_and_user_doesnt_exist(self):
        entry = DictStorageModel(key='bar-old.user', value='{}')
        self.session.add(entry)
        migrator = DictstorageMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move', strict=False)

        migrator.migrate()
        self.assertEquals('bar-doesnt.exist', entry.key)

    def test_returns_proper_results_for_moving_keys(self):
        entry = DictStorageModel(key='baz-old.user', value='{}')
        self.session.add(entry)
        migrator = DictstorageMigrator(
            self.portal, {'old.user': 'new.user'}, 'move', strict=False)

        results = migrator.migrate()
        self.assertIn(
            ('baz-old.user', 'old.user', 'new.user'),
            results['keys']['moved']
        )
