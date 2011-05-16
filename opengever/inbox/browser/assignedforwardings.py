"""Contains a View wich shows all assigned Forwardings"""
from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class InboxAssignedForwardings(GlobalTaskListingTab):
    """Listing tab for listing all tasks which are assigned to this inbox.
    """

    grok.name('tabbedview_view-assigned_forwardings')
    grok.context(IInbox)

    displayStates = 'forwarding-state-open'

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        principal = 'inbox:%s' % get_client_id()

        # Get the current client's ID
        registry = getUtility(IRegistry)
        client_config = registry.forInterface(IClientConfiguration)
        current_client_id = client_config.client_id

        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(
                    principal, self.sort_on, self.sort_order).filter(
                        Task.review_state == self.displayStates).filter(
                            Task.client_id != current_client_id)
        return query