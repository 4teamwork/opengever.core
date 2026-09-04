"""
This module contains the background tasks control panel and its listing tab.
"""

from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table import helper
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_FAILED
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.model import TASK_STATUS_RUNNING
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import _
from opengever.tabbedview import FilteredListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from sqlalchemy.sql.expression import false
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


STATUS_LABELS = {
    TASK_STATUS_PENDING: _(u'label_background_task_status_pending',
                           default=u'Pending'),
    TASK_STATUS_RUNNING: _(u'label_background_task_status_running',
                           default=u'Running'),
    TASK_STATUS_SUCCEEDED: _(u'label_background_task_status_succeeded',
                             default=u'Succeeded'),
    TASK_STATUS_FAILED: _(u'label_background_task_status_failed',
                          default=u'Failed'),
}


def readable_datetime(item, value):
    """Helper rendering a nullable datetime column.

    `started` and `finished` are NULL as long as a task has not reached the
    respective stage, which must not blow up the listing.
    """
    if value is None:
        return u''
    return helper.readable_date_time(item, value)


def status_helper(item, value):
    """Helper for displaying a task status in human readable form.
    """
    label = STATUS_LABELS.get(value)
    if label is None:
        return value
    return translate(label, context=getRequest())


class IBackgroundTasksTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configuration using the background
    tasks model as source.
    """


class StatusFilter(Filter):
    """Filter to only display background tasks with a specific status."""

    def __init__(self, id, label, status, default=False):
        super(StatusFilter, self).__init__(id, label, default=default)
        self.status = status

    def update_query(self, query):
        return query.filter(BackgroundTask.status == self.status)


class NotSucceededFilter(Filter):
    """Filter to hide background tasks which have completed successfully."""

    def update_query(self, query):
        return query.filter(BackgroundTask.status != TASK_STATUS_SUCCEEDED)


@implementer(IBackgroundTasksTableSourceConfig)
class BackgroundTasksListing(FilteredListingTab):
    """Lists the background tasks of the current admin unit.

    `FilteredListingTab` (and not `BaseListingTab`) is the base class on
    purpose: it renders `generic_with_filters.pt`, which keeps the status
    filters reachable when the listing is empty. With the plain
    `generic.pt` the whole container - and with it the filters - is omitted
    as soon as there are no contents, which would trap the user on the
    default "not succeeded" filter on a healthy system where every task has
    succeeded.
    """

    sort_on = 'created'
    sort_reverse = True

    # the model attributes is used for a dynamic textfiltering functionality
    model = BackgroundTask
    show_selects = False
    enabled_actions = []
    major_actions = []

    filterlist_name = 'background_task_status_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', _(u'label_tabbedview_filter_all')),

        NotSucceededFilter(
            'filter_not_succeeded',
            _(u'label_background_tasks_filter_not_succeeded',
              default=u'Not succeeded'),
            default=True),

        StatusFilter('filter_pending',
                     STATUS_LABELS[TASK_STATUS_PENDING],
                     TASK_STATUS_PENDING),

        StatusFilter('filter_running',
                     STATUS_LABELS[TASK_STATUS_RUNNING],
                     TASK_STATUS_RUNNING),

        StatusFilter('filter_succeeded',
                     STATUS_LABELS[TASK_STATUS_SUCCEEDED],
                     TASK_STATUS_SUCCEEDED),

        StatusFilter('filter_failed',
                     STATUS_LABELS[TASK_STATUS_FAILED],
                     TASK_STATUS_FAILED),
    )

    columns = (
        {'column': 'created',
         'column_title': _(u'label_background_task_created',
                           default=u'Created'),
         'transform': readable_datetime},

        {'column': 'started',
         'column_title': _(u'label_background_task_started',
                           default=u'Started'),
         'transform': readable_datetime},

        {'column': 'finished',
         'column_title': _(u'label_background_task_finished',
                           default=u'Finished'),
         'transform': readable_datetime},

        {'column': 'task_id',
         'column_title': _(u'label_background_task_id',
                           default=u'Task ID')},

        {'column': 'task_type',
         'column_title': _(u'label_background_task_type',
                           default=u'Task type')},

        {'column': 'status',
         'column_title': _(u'label_background_task_status',
                           default=u'Status'),
         'transform': status_helper},
    )

    def get_base_query(self):
        """Returns the base search query (sqlalchemy).

        The listing is always restricted to the current admin unit. This
        restriction lives in the base query on purpose, so that no filter is
        able to widen it.
        """
        admin_unit = get_current_admin_unit()
        if admin_unit is None:
            return BackgroundTask.query.filter(false())

        return BackgroundTask.query.by_admin_unit(admin_unit.unit_id)


@implementer(ITableSource)
@adapter(IBackgroundTasksTableSourceConfig, Interface)
class BackgroundTasksTableSource(SqlTableSource):
    """Table source for background tasks.
    """

    # `status` is deliberately not searchable: it is rendered translated,
    # so a text search would never match what the user sees. The status
    # filters cover that need.
    searchable_columns = [BackgroundTask.task_id,
                          BackgroundTask.task_type]


class BackgroundTasksControlPanel(TabbedView):
    """Control panel tabbed view listing the background tasks.
    """

    tabs = [
        {'id': 'bgtasks-cp-tasks',
         'icon': None,
         'url': '#',
         'class': None},
    ]

    def get_tabs(self):
        return self.tabs

    def render(self):
        return TabbedView.__call__(self)
