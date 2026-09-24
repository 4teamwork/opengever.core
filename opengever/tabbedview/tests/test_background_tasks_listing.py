from datetime import datetime
from ftw.testbrowser import browsing
from mock import patch
from opengever.base.model import create_session
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_ALL
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview.browser.backgroundtasks import BackgroundTasksListing
from opengever.tabbedview.browser.backgroundtasks import STATUS_LABELS
from opengever.testing import IntegrationTestCase
import transaction


class TestBackgroundTasksListing(IntegrationTestCase):
    """Tests for the background tasks control panel listing."""

    def setUp(self):
        super(TestBackgroundTasksListing, self).setUp()
        self.login(self.manager)
        self.admin_unit_id = get_current_admin_unit().unit_id
        self.known_task_ids = []
        self.clear_tasks()

    def clear_tasks(self):
        create_session().query(BackgroundTask).delete()
        transaction.commit()

    def create_task(self, task_id, status=TASK_STATUS_PENDING,
                    task_type=u'dummy', admin_unit_id=None, created=None,
                    started=None, finished=None):
        task = BackgroundTask()
        task.task_id = task_id
        task.admin_unit_id = admin_unit_id or self.admin_unit_id
        task.task_type = task_type
        task.status = status
        task.priority = 5
        task.created = created or datetime(2026, 9, 1, 8, 0)
        task.started = started
        task.finished = finished
        task.retries = 0
        task.max_retries = 3
        create_session().add(task)
        transaction.commit()
        self.known_task_ids.append(task_id)
        return task

    def create_task_per_status(self):
        for status in TASK_STATUS_ALL:
            self.create_task(u'task-%s' % status, status=status)

    def open_listing(self, browser, **data):
        self.login(self.manager, browser)
        browser.open(self.portal, view='tabbedview_view-bgtasks-cp-tasks',
                     data=data)

    def listing_rows(self, browser):
        """Returns the data rows (without the header row) of the listing."""
        return browser.css('.listing').first.lists()[1:]

    def listed_task_ids(self, browser):
        """Returns the task ids of the listed rows, in listing order.

        Looking the ids up cell by cell keeps the assertion independent of
        the column offset of the rendered table. Task ids are unique enough
        that a cell matching one is always the task_id cell.
        """
        task_ids = []
        for row in self.listing_rows(browser):
            for cell in row:
                if cell in self.known_task_ids:
                    task_ids.append(cell)
        return task_ids

    @browsing
    def test_hides_succeeded_tasks_by_default(self, browser):
        self.create_task_per_status()

        self.open_listing(browser)

        self.assertItemsEqual(
            [u'task-pending', u'task-running', u'task-failed'],
            self.listed_task_ids(browser))

    @browsing
    def test_status_filter_limits_listing_to_that_status(self, browser):
        self.create_task_per_status()

        self.open_listing(
            browser, background_task_status_filter='filter_succeeded')

        self.assertEqual([u'task-succeeded'], self.listed_task_ids(browser))

    @browsing
    def test_all_filter_lists_every_task(self, browser):
        self.create_task_per_status()

        self.open_listing(
            browser, background_task_status_filter='filter_all')

        self.assertItemsEqual(
            [u'task-pending', u'task-running', u'task-succeeded',
             u'task-failed'],
            self.listed_task_ids(browser))

    @browsing
    def test_tasks_of_other_admin_units_are_never_listed(self, browser):
        self.create_task(u'own-task')
        self.create_task(u'foreign-task', admin_unit_id=u'other-unit')

        self.open_listing(browser)
        self.assertEqual([u'own-task'], self.listed_task_ids(browser))

        self.open_listing(
            browser, background_task_status_filter='filter_all')
        self.assertEqual([u'own-task'], self.listed_task_ids(browser))

    @browsing
    def test_tasks_are_sorted_by_created_descending(self, browser):
        self.create_task(u'oldest', created=datetime(2026, 9, 1, 8, 0))
        self.create_task(u'newest', created=datetime(2026, 9, 3, 8, 0))
        self.create_task(u'middle', created=datetime(2026, 9, 2, 8, 0))

        self.open_listing(browser)

        self.assertEqual([u'newest', u'middle', u'oldest'],
                         self.listed_task_ids(browser))

    @browsing
    def test_unfinished_tasks_render_empty_date_cells(self, browser):
        self.create_task(u'pending-task', status=TASK_STATUS_PENDING)

        self.open_listing(browser)

        rows = [row for row in self.listing_rows(browser)
                if u'pending-task' in row]
        self.assertEqual(1, len(rows))

        # `started` and `finished` are the two cells preceding `task_id` and
        # are still NULL for a task that has not been picked up yet.
        row = rows[0]
        task_id_index = row.index(u'pending-task')
        self.assertEqual([u'', u''], row[task_id_index - 2:task_id_index])

    @browsing
    def test_control_panel_renders_the_background_tasks_tab(self, browser):
        self.create_task(u'pending-task')
        self.login(self.manager, browser)

        browser.open(self.portal, view='background-tasks-controlpanel')

        self.assertEqual(1, len(browser.css('.listing')))

    @browsing
    def test_control_panel_requires_manage_portal(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(self.portal, view='background-tasks-controlpanel')

    def test_configlet_is_registered(self):
        action_ids = [action.getId() for action
                      in self.portal.portal_controlpanel.listActions()]

        self.assertIn('background-tasks-controlpanel', action_ids)

    def test_columns_are_defined_in_the_expected_order(self):
        self.assertEqual(
            ['created', 'started', 'finished', 'task_id', 'task_type',
             'status'],
            [column['column'] for column in BackgroundTasksListing.columns])

    def test_filterlist_offers_a_filter_per_status(self):
        filter_ids = list(BackgroundTasksListing.filterlist.keys())

        self.assertEqual(
            ['filter_all', 'filter_not_succeeded', 'filter_pending',
             'filter_running', 'filter_succeeded', 'filter_failed'],
            filter_ids)
        self.assertEqual(
            ['filter_%s' % status for status in TASK_STATUS_ALL],
            [filter_id for filter_id in filter_ids
             if filter_id not in ('filter_all', 'filter_not_succeeded')])

    def test_filters_stay_reachable_when_the_listing_is_empty(self):
        # `generic_with_filters.pt` renders the status filters even when
        # there are no contents. With the plain `generic.pt` an empty
        # default filter would leave no way back to the succeeded tasks.
        self.assertTrue(
            BackgroundTasksListing.template.filename.endswith(
                'generic_with_filters.pt'),
            'Listing must render the template that keeps filters reachable '
            'on an empty result, got %r' % (
                BackgroundTasksListing.template.filename,))

    def test_not_succeeded_is_the_default_filter(self):
        self.assertEqual(
            'filter_not_succeeded',
            BackgroundTasksListing.filterlist.default_filter.id)

    def test_listing_is_read_only(self):
        self.assertFalse(BackgroundTasksListing.show_selects)
        self.assertEqual([], BackgroundTasksListing.enabled_actions)
        self.assertEqual([], BackgroundTasksListing.major_actions)

    def test_sorts_by_created_descending(self):
        self.assertEqual('created', BackgroundTasksListing.sort_on)
        self.assertTrue(BackgroundTasksListing.sort_reverse)

    def test_every_status_has_a_label(self):
        self.assertItemsEqual(TASK_STATUS_ALL, STATUS_LABELS.keys())

    @browsing
    def test_listing_is_empty_without_a_configured_admin_unit(self, browser):
        self.create_task(u'orphan-task')

        with patch('opengever.tabbedview.browser.backgroundtasks.'
                   'get_current_admin_unit', return_value=None):
            self.open_listing(browser)

        self.assertEqual(200, browser.status_code)
        self.assertEqual([], self.listed_task_ids(browser))

    @browsing
    def test_listing_view_requires_manage_portal(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(self.portal,
                         view='tabbedview_view-bgtasks-cp-tasks')

    @browsing
    def test_foreign_tasks_are_hidden_under_every_status_filter(self, browser):
        for status in TASK_STATUS_ALL:
            self.create_task(u'foreign-%s' % status, status=status,
                             admin_unit_id=u'other-unit')

        for status in TASK_STATUS_ALL:
            self.open_listing(
                browser,
                background_task_status_filter='filter_%s' % status)
            self.assertEqual([], self.listed_task_ids(browser))

    @browsing
    def test_listing_renders_one_column_per_configured_column(self, browser):
        self.create_task(u'pending-task')

        self.open_listing(browser)

        header = browser.css('.listing').first.lists()[0]
        self.assertEqual(len(BackgroundTasksListing.columns), len(header))

    def test_configlet_points_to_the_control_panel(self):
        actions = dict(
            (action.getId(), action)
            for action in self.portal.portal_controlpanel.listActions())

        configlet = actions['background-tasks-controlpanel']
        self.assertEqual('Background Tasks Control Panel', configlet.title)
        self.assertEqual(
            'string:${portal_url}/@@background-tasks-controlpanel',
            configlet.url_expr)
