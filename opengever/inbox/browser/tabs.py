from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.inbox.inbox import IInbox
from opengever.inbox.yearfolder import IYearFolder
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tabs import Tasks
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from zope.component import getUtility


def get_current_inbox_principal(context):

    return 'inbox:%s' % get_client_id()


class AssignedInboxTasks(GlobalTaskListingTab):
    """Listing of tasks (including forwardings) which the
    responsible is the current inbox."""

    grok.name('tabbedview_view-assigned_inbox_tasks')
    grok.require('zope2.View')
    grok.context(IInbox)

    def get_base_query(self):
        """Returns the base search query (sqlalchemy),
        wich only select tasks assigned to the current inbox.
        """

        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(
            get_current_inbox_principal(self.context),
            self.sort_on,
            self.sort_order)

        return query


class IssuedInboxTasks(Tasks):
    """Listing of local tasks (including forwardings) which the
    issuer is the current inbox."""

    grok.name('tabbedview_view-issued_inbox_tasks')
    grok.require('zope2.View')
    grok.context(IInbox)

    search_options = {'issuer': get_current_inbox_principal}

    types = ['opengever.task.task', 'opengever.inbox.forwarding']

    @property
    def columns(self):
        """Drop the containing_subdossier column from the column list
        """
        remove_columns = ['containing_subdossier', ]
        columns = []

        for col in super(IssuedInboxTasks, self).columns:
            if col.get('column') not in remove_columns:
                columns.append(col)

        return columns

    def update_config(self):
        """Remove the default path filter to the current context.
        It should search tasks over the complete client."""

        super(IssuedInboxTasks, self).update_config()
        self.filter_path = None


class ClosedForwardings(Tasks):

    grok.name('tabbedview_view-closed-forwardings')
    grok.context(IYearFolder)
    grok.require('zope2.View')

    types = ['opengever.inbox.forwarding', ]
    enabled_actions = []
    major_actions = []
