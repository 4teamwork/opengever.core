from opengever.globalindex import Session
from opengever.globalindex.handlers.task import sync_task
from opengever.globalindex.query import TaskQuery
from opengever.task import _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
import transaction
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class ClearAndRebuildTasks(BrowserView):
    """Default view for a category. Shows all contained items and categories.
    """

    def __call__(self):
        ptool = getToolByName(self, 'plone_utils')
        catalog = getToolByName(self, 'portal_catalog')
        session = Session()

        # Get the current client's ID
        registry = getUtility(IRegistry)
        client_config = registry.forInterface(IClientConfiguration)
        client_id = client_config.client_id

        # Get all tasks and forwardings currently in the global index
        task_query = TaskQuery()
        indexed_tasks = task_query.get_tasks_for_client(client=client_id)

        # Clear existing tasks in global index that have been created on this client
        for task in indexed_tasks:
            session.delete(task)
        transaction.commit()

        # Get tasks and forwardings that need to be reindexed from catalog
        cataloged_tasks = catalog(portal_type="opengever.task.task")
        forwardings = catalog(portal_type="opengever.inbox.forwarding")
        objs_to_reindex = cataloged_tasks + forwardings

        # Re-Index tasks
        for obj in objs_to_reindex:
            sync_task(obj.getObject(), None)

        ptool.addPortalMessage(
            _("Global task index has been cleared (${cleared}) and rebuilt (${rebuilt})",
                  mapping = {'cleared': len(indexed_tasks),
                             'rebuilt': len(objs_to_reindex)}),
              type="info")

        return self.context.REQUEST.RESPONSE.redirect(self.context.absolute_url()
                                        + '/@@ogds-controlpanel#ogds-cp-alltasks')


