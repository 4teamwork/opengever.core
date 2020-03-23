from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from plone import api
import transaction


class TestIntegrationTestSetup(IntegrationTestCase):

    def test_zodb_changes_are_isolated_1(self):
        self.login(self.administrator)
        self.assertEquals(
            'Ordnungssystem', self.repository_root.Title(),
            'ZODB changes seem not to be isolated between tests.')
        self.repository_root.title_de = 'Changed Repository Root Title'
        self.assertEquals('Changed Repository Root Title',
                          self.repository_root.Title())

    # By duplicating the method pointer on the class this test will be
    # executed twice. The test is built so that it detects leaks from
    # a prior run when the isolation does not work.
    test_zodb_changes_are_isolated_2 = test_zodb_changes_are_isolated_1

    def test_sql_changes_are_isolated_1(self):
        self.login(self.administrator)
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

    # By duplicating the method pointer on the class this test will be
    # executed twice. The test is built so that it detects leaks from
    # a prior run when the isolation does not work.
    test_sql_changes_are_isolated_2 = test_sql_changes_are_isolated_1

    def test_rollback_nested_sql_savepoints(self):
        self.login(self.administrator)
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

    def test_serverside_default_user_is_anonymous(self):
        self.assertTrue(api.user.is_anonymous())

    @browsing
    def test_preparing_changes_do_not_trigger_csrf_protection(self, browser):
        self.login(self.administrator, browser)
        self.repository_root.title_de = 'New Repository Root Title'
        browser.open(self.repository_root)
        self.assertEquals('New Repository Root Title', plone.first_heading())
