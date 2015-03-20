from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import obj2brain
from opengever.usermigration.dossier import DossierMigrator
from opengever.usermigration.exceptions import UserMigrationException
from plone import api


class TestDossierMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestDossierMigrator, self).setUp()
        self.portal = self.layer['portal']
        self.catalog = api.portal.get_tool('portal_catalog')

        self.old_user = create(Builder('ogds_user').id('old.user'))
        self.new_user = create(Builder('ogds_user').id('new.user'))

        self.dossier = create(Builder('dossier')
                              .titled(u'Testdossier')
                              .having(responsible='old.user'))

    def test_dossier_responsible_gets_migrated(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()
        self.assertEquals('new.user', IDossier(self.dossier).responsible)

    def test_dossier_responsible_index_gets_updated(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()

        # Index should be up to date
        brains = self.catalog(responsible='new.user')
        self.assertEquals(1, len(brains))

        # Metadata should be up to date
        self.assertEquals('new.user', obj2brain(self.dossier).responsible)

    def test_raises_if_strict_and_user_doesnt_exist(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move')

        with self.assertRaises(UserMigrationException):
            migrator.migrate()

    def test_doesnt_raise_if_not_strict_and_user_doesnt_exist(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move', strict=False)

        migrator.migrate()
        self.assertEquals('doesnt.exist', IDossier(self.dossier).responsible)

    def test_returns_proper_results_for_moving_responsible(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        results = migrator.migrate()

        self.assertEquals(
            [('/plone/dossier-1', 'old.user', 'new.user')],
            results['responsible']['moved']
        )
