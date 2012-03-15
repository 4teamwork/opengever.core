from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from opengever.globalindex import Session
from opengever.globalindex.handlers.task import index_task
from opengever.globalindex.interfaces import IGlobalindexMaintenanceView
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.ogds.base.exceptions import ClientNotFound
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task.task import ITask
from time import strftime
from urllib2 import URLError
from zope.component import getUtility
from zope.interface import implements
from zope.intid.interfaces import IIntIds
import os
import requests


class GlobalindexMaintenanceView(BrowserView):
    """A view wich completly reindex all local tasks in the globalindex"""

    implements(IGlobalindexMaintenanceView)

    def mklog(self):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write

        def log(msg, timestamp=True):
            if timestamp:
                msg = strftime('%Y/%m/%d-%H:%M:%S ') + msg
            write(msg.encode('utf-8'))
        return log

    def global_reindex(self):
        """ """

        delimiter = "-" * 100 + "\n"
        self.request.RESPONSE.write(
            "%s\n\nGlobalindex maintanance view\n"
            "%s\n\nMethods:reindex, localreindex\n%s" %
            (3 * delimiter, delimiter, 3 * delimiter))

        info = getUtility(IContactInformation)
        for client in info.get_clients():
            try:

                self.request.RESPONSE.write(
                    '----Start reindexing tasks from %s----\n' % (
                        client.title.encode('utf-8')))

                self._sync_remote_request(
                    client.client_id,
                    '@@globalindex-maintenance/local_reindex',)

                self.request.RESPONSE.write(
                    '----Finished reindexing tasks from %s --- \n\n\n ----' % (
                        client.title.encode('utf-8')))

            except URLError, e:
                return '----Failed reindexing tasks from %s\n %s ---' % (
                    client.title, e)

    def _sync_remote_request(
        self, target_client_id, viewname, path='', data={}, headers={}):

        if get_client_id() == target_client_id:
            self.local_reindex()
        else:
            info = getUtility(IContactInformation)
            target = info.get_client_by_id(target_client_id)

            if not target:
                raise ClientNotFound()

            headers = headers.copy()
            data = data.copy()

            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()

            key = 'X-OGDS-AC'
            if key not in headers.keys() and member:
                headers[key] = member.getId()

            headers['X-OGDS-CID'] = get_client_id()

            viewname = viewname.startswith(
                '@@') and viewname or '@@%s' % viewname
            if path:
                url = os.path.join(target.site_url, path, viewname)
            else:
                url = os.path.join(target.site_url, viewname)

            r = requests.post(url, data=data, headers=headers)

            for line in r.iter_lines():
                self.context.REQUEST.RESPONSE.write('%s\n' % line)

    def local_reindex(self):
        """Reindex all local tasks."""

        query = getUtility(ITaskQuery)
        intids = getUtility(IIntIds)

        # Get all tasks and forwardings currently in the global index
        indexed_tasks = [task.int_id for task in query.get_tasks_for_client(
                client=get_client_id())]

        catalog = getToolByName(self, 'portal_catalog')
        tasks = catalog(object_provides=ITask.__identifier__)
        log = self.mklog()

        # Update the existing tasks
        for task in tasks:
            obj = task.getObject()
            int_id = intids.getId(obj)
            index_task(obj, None)
            if int_id in indexed_tasks:
                indexed_tasks.remove(int_id)
            log('Obj %s updated in the globalindex.\n' % (obj))

        # Clear tasks in the globalindex who's not-existing anymore.
        if len(indexed_tasks):
            for int_id in indexed_tasks:
                task = query.get_task_by_oguid('%s:%i' % (
                        get_client_id(), int_id))

                log('ERROR: Task(%s) with the id: %i does not exist in the'
                    'catalog. It should be manually removed.\n' % (
                        task, task.task_id)
                    )
        return True

    def check_predecessor_sync(self):
        """Method wich checks the synchronisation between
        predecessors and successors"""

        log = self.mklog()
        successors = Session().query(Task).filter(Task.predecessor != None)

        info = getUtility(IContactInformation)

        sync_problems_counter = 0

        for successor in successors:
            predecessor = successor.predecessor

            # check review_state
            if (predecessor.review_state != successor.review_state and
                predecessor.review_state != u'forwarding-state-closed'):

                client = info.get_client_by_id(predecessor.client_id)
                predecessor_url = ' - %s\n   State: %s\n   Url: %s/%s' % (
                    predecessor.title,
                    predecessor.review_state,
                    client.public_url,
                    predecessor.physical_path)

                client = info.get_client_by_id(successor.client_id)
                successor_url = ' - %s\n   State: %s\n   Url: %s/%s' % (
                    successor.title,
                    successor.review_state,
                    client.public_url,
                    successor.physical_path)

                log("State synchronisation invalid:\n%s\n%s\n\n" % (
                    predecessor_url, successor_url))

                sync_problems_counter += 1

        log('Predecessor synchronisation check finished:'
            '\n  %i Problems detected' % (sync_problems_counter))
