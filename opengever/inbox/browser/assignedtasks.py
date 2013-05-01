"""Contains the view for Assigned Tasks"""
from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from zope.component import getUtility


class InboxAssignedTasks(GlobalTaskListingTab):
    """Displays all Forwardings that are assigned to the Inbox
    """
    grok.name('tabbedview_view-assigned_tasks')
    grok.context(IInbox)

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        principal = 'inbox:%s' % get_client_id()
        query_util = getUtility(ITaskQuery)

        # show all tasks assigned to this client's inbox
        query = query_util._get_tasks_for_responsible_query(principal,
                                                            self.sort_on,
                                                            self.sort_order)

        # .. and assigned to the current client
        query = query.filter_by(assigned_client=get_client_id())
        return query