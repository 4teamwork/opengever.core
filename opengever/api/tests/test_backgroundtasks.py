from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_FAILED
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_RUNNING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestBackgroundTasksGet(IntegrationTestCase):

    def create_task(self, status=TASK_STATUS_PENDING, admin_unit_id=None,
                    created=None, task_type=u'dummy', **kwargs):
        task = BackgroundTask(
            admin_unit_id=admin_unit_id or get_current_admin_unit().unit_id,
            task_type=task_type,
            status=status,
            created=created or datetime(2026, 1, 1),
            **kwargs)
        create_session().add(task)
        create_session().flush()
        return task

    def get_task_ids(self, browser, query=''):
        browser.open(self.portal, view='@backgroundtasks' + query,
                     headers=self.api_headers)
        return [item['@id'].split('/')[-1] for item in browser.json['items']]

    @browsing
    def test_requires_manage_portal_permission(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error():
            browser.open(self.portal, view='@backgroundtasks',
                         headers=self.api_headers)

    @browsing
    def test_default_hides_succeeded_tasks(self, browser):
        self.login(self.manager, browser=browser)
        pending = self.create_task(TASK_STATUS_PENDING)
        running = self.create_task(TASK_STATUS_RUNNING)
        failed = self.create_task(TASK_STATUS_FAILED)
        self.create_task(TASK_STATUS_SUCCEEDED)

        self.assertItemsEqual(
            [pending.task_id, running.task_id, failed.task_id],
            self.get_task_ids(browser))
        self.assertEqual(3, browser.json['items_total'])

    @browsing
    def test_status_filter(self, browser):
        self.login(self.manager, browser=browser)
        self.create_task(TASK_STATUS_PENDING)
        succeeded = self.create_task(TASK_STATUS_SUCCEEDED)

        self.assertEqual(
            [succeeded.task_id],
            self.get_task_ids(browser, '?filters.status:record:list=succeeded'))

    @browsing
    def test_multiple_status_filters(self, browser):
        self.login(self.manager, browser=browser)
        pending = self.create_task(TASK_STATUS_PENDING)
        failed = self.create_task(TASK_STATUS_FAILED)
        self.create_task(TASK_STATUS_RUNNING)

        self.assertItemsEqual(
            [pending.task_id, failed.task_id],
            self.get_task_ids(
                browser,
                '?filters.status:record:list=pending'
                '&filters.status:record:list=failed'))

    @browsing
    def test_unknown_status_is_rejected(self, browser):
        self.login(self.manager, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(
                self.portal,
                view='@backgroundtasks?filters.status:record:list=bogus',
                headers=self.api_headers)

    @browsing
    def test_task_type_filter(self, browser):
        self.login(self.manager, browser=browser)
        self.create_task(task_type=u'dummy')
        move = self.create_task(task_type=u'move')
        reindex = self.create_task(task_type=u'reindex')

        self.assertEqual(
            [move.task_id],
            self.get_task_ids(browser, '?filters.task_type:record:list=move'))
        self.assertItemsEqual(
            [move.task_id, reindex.task_id],
            self.get_task_ids(
                browser,
                '?filters.task_type:record:list=move'
                '&filters.task_type:record:list=reindex'))

    @browsing
    def test_defaults_to_current_admin_unit(self, browser):
        self.login(self.manager, browser=browser)
        own = self.create_task(admin_unit_id=None)
        self.create_task(admin_unit_id=u'other')

        self.assertEqual([own.task_id], self.get_task_ids(browser))

    @browsing
    def test_admin_unit_filter(self, browser):
        self.login(self.manager, browser=browser)
        self.create_task(admin_unit_id=None)
        other = self.create_task(admin_unit_id=u'other')

        self.assertEqual(
            [other.task_id],
            self.get_task_ids(browser, '?filters.admin_unit:record:list=other'))

    @browsing
    def test_sorted_by_created_descending(self, browser):
        self.login(self.manager, browser=browser)
        old = self.create_task(created=datetime(2026, 1, 1))
        new = self.create_task(created=datetime(2026, 3, 1))
        middle = self.create_task(created=datetime(2026, 2, 1))

        self.assertEqual(
            [new.task_id, middle.task_id, old.task_id],
            self.get_task_ids(browser))

    @browsing
    def test_batching(self, browser):
        self.login(self.manager, browser=browser)
        for day in range(1, 4):
            self.create_task(created=datetime(2026, 1, day))

        self.get_task_ids(browser, '?b_size=2')
        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(3, browser.json['items_total'])
        self.assertEqual(2, browser.json['b_size'])
        self.assertIn('next', browser.json['batching'])

    @browsing
    def test_item_representation(self, browser):
        self.login(self.manager, browser=browser)
        task = self.create_task(
            TASK_STATUS_FAILED, created=datetime(2026, 1, 1, 12, 0),
            retries=2, error_message=u'Boom')

        browser.open(self.portal, view='@backgroundtasks',
                     headers=self.api_headers)
        item, = browser.json['items']

        self.assertEqual(
            u'http://nohost/plone/@backgroundtasks/{}'.format(task.task_id),
            item['@id'])
        self.assertEqual(u'virtual.ogds.backgroundtask', item['@type'])
        self.assertEqual(u'failed', item['status'])
        self.assertEqual(u'dummy', item['task_type'])
        self.assertEqual(get_current_admin_unit().unit_id, item['admin_unit'])
        self.assertEqual(2, item['retries'])
        self.assertEqual(u'Boom', item['error_message'])
        self.assertTrue(item['created'].endswith('+00:00'), item['created'])
        self.assertIsNone(item['started'])
        self.assertIsNone(item['finished'])
