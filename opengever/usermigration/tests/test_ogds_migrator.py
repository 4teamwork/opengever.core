from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.service import ogds_service
from opengever.testing import FunctionalTestCase
from opengever.usermigration.exceptions import UserMigrationException
from opengever.usermigration.ogds import OGDSMigrator


class TestOGDSMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestOGDSMigrator, self).setUp()
        self.portal = self.layer['portal']

        self.new_users_group = create(Builder('ogds_group')
                                      .id('new_users_group'))
        self.new_inbox_group = create(Builder('ogds_group')
                                      .id('new_inbox_group'))

    def test_users_group_gets_migrated(self):
        org_unit_id = self.org_unit.unit_id
        migrator = OGDSMigrator(
            self.portal, {'org-unit-1_users': 'new_users_group'}, 'move')
        migrator.migrate()

        org_unit = ogds_service().fetch_org_unit(org_unit_id)
        self.assertEquals('new_users_group', org_unit.users_group.groupid)

    def test_inbox_group_gets_migrated(self):
        org_unit_id = self.org_unit.unit_id
        migrator = OGDSMigrator(
            self.portal, {'org-unit-1_inbox_users': 'new_inbox_group'}, 'move')
        migrator.migrate()

        org_unit = ogds_service().fetch_org_unit(org_unit_id)
        self.assertEquals('new_inbox_group', org_unit.inbox_group.groupid)

    def test_raises_if_group_doesnt_exist(self):
        migrator = OGDSMigrator(
            self.portal, {'org-unit-1_users': 'doesnt.exist'}, 'move')

        with self.assertRaises(UserMigrationException):
            migrator.migrate()

    def test_returns_proper_results_for_moving_users_group(self):
        migrator = OGDSMigrator(
            self.portal, {'org-unit-1_users': 'new_users_group'}, 'move')
        results = migrator.migrate()

        self.assertEquals(
            [('<OrgUnit org-unit-1>', 'org-unit-1_users', 'new_users_group')],
            results['users_groups']['moved']
        )

    def test_returns_proper_results_for_moving_inbox_group(self):
        migrator = OGDSMigrator(
            self.portal, {'org-unit-1_inbox_users': 'new_inbox_group'}, 'move')
        results = migrator.migrate()

        self.assertEquals(
            [('<OrgUnit org-unit-1>', 'org-unit-1_inbox_users', 'new_inbox_group')],
            results['inbox_groups']['moved']
        )
