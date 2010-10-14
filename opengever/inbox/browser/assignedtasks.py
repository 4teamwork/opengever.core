from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingMixin
from opengever.inbox.inbox import IInbox
from zope.component import getUtility


class InboxAssignedTasks(GlobalTaskListingMixin, OpengeverListingTab):
    """Listing tab for listing all tasks which are assigned to this inbox.
    """

    grok.name('tabbedview_view-assigned_tasks')
    grok.context(IInbox)

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        principal = 'inbox:%s' % get_client_id()

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_responsible_query(principal,
                                                           self.sort_on,
                                                           self.sort_order)
