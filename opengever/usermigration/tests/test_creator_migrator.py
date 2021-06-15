from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing.helpers import obj2brain
from opengever.usermigration.creator import CreatorMigrator
from opengever.usermigration.exceptions import UserMigrationException
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME


class TestCreatorMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestCreatorMigrator, self).setUp()
        self.portal = self.layer['portal']
        self.catalog = api.portal.get_tool('portal_catalog')

        create_plone_user(self.portal, 'old.user')
        setRoles(self.portal, 'old.user', ['Reader', 'Contributor'])

        create_plone_user(self.portal, 'new.user')
        setRoles(self.portal, 'new.user', ['Reader', 'Contributor'])

        self.login(user_id='old.user')
        self.dossier = create(Builder('dossier')
                              .titled(u'Testdossier'))

        self.doc = create(Builder('document')
                          .within(self.dossier))

        self.login(user_id=TEST_USER_NAME)

    def test_creators_get_migrated(self):
        migrator = CreatorMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()
        self.assertEquals(('new.user',), self.dossier.creators)
        self.assertEquals(('new.user',), self.doc.creators)

    def test_uppercase_creator_accessor_works_after_migration(self):
        migrator = CreatorMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()
        self.assertEquals('new.user', self.dossier.Creator())
        self.assertEquals('new.user', self.doc.Creator())

    def test_creator_index_gets_updated(self):
        migrator = CreatorMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()

        # Index should be up to date
        self.assertEquals('new.user',
                          index_data_for(self.dossier).get('Creator'))
        self.assertEquals('new.user',
                          index_data_for(self.doc).get('Creator'))

        # Metadata should be up to date
        self.assertEquals(('new.user', ), obj2brain(self.dossier).listCreators)
        self.assertEquals(('new.user', ), obj2brain(self.doc).listCreators)

        self.assertEquals('new.user', obj2brain(self.dossier).Creator)
        self.assertEquals('new.user', obj2brain(self.doc).Creator)

    def test_raises_if_user_doesnt_exist(self):
        migrator = CreatorMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move')

        with self.assertRaises(UserMigrationException):
            migrator.migrate()

    def test_returns_proper_results_for_moving_creator(self):
        migrator = CreatorMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        results = migrator.migrate()

        self.assertEquals(
            [
                ('/plone/dossier-1', 'old.user', 'new.user'),
                ('/plone/dossier-1/document-1', 'old.user', 'new.user'),
            ],
            results['creators']['moved']
        )
