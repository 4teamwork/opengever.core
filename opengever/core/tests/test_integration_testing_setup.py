from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.utils import ogds_service
from opengever.testing import IntegrationTestCase
import transaction


class TestIntegrationTestSetup(IntegrationTestCase):

    def test_zodb_changes_are_isolated_1(self):
        self.assertEquals(
            'Repository Root', self.repository_root.Title(),
            'ZODB changes seem not to be isolated between tests.')
        self.repository_root.title_de = 'Changed Repository Root Title'
        self.assertEquals('Changed Repository Root Title',
                          self.repository_root.Title())

    test_zodb_changes_are_isolated_2 = test_zodb_changes_are_isolated_1

    def test_sql_changes_are_isolated_1(self):
        args = {
            'firstname': u'Leak',
            'lastname': u'Officer',
            'userid': 'leak.officer',
            'email': 'leak@officer.local',
        }
        self.assertFalse(
            ogds_service().fetch_user(args['userid']),
            'SQL changes seem not to be isolated between tests.')
        create(Builder('ogds_user').having(**args))
        self.assertTrue(ogds_service().fetch_user(args['userid']))

    test_sql_changes_are_isolated_2 = test_sql_changes_are_isolated_1

    def test_rollback_nested_sql_savepoints(self):
        args = {
            'firstname': u'Transaction',
            'lastname': u'Manager',
            'userid': 'transaction.manager',
        }
        self.assertFalse(
            ogds_service().fetch_user(args['userid']),
            'Opps, there is already a user {!r}'.format(args['userid']))

        savepoint = transaction.savepoint()
        create(Builder('ogds_user').having(**args))
        self.assertTrue(ogds_service().fetch_user(args['userid']))
        savepoint.rollback()
        self.assertFalse(
            ogds_service().fetch_user(args['userid']),
            'Could not rollback SQL properly.')
