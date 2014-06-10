from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.utils import get_client_id
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified


class SuccessorTaskController(grok.Adapter):
    """The successor task controller manages predecessor and successor
    references between tasks.
    """

    grok.provides(ISuccessorTaskController)
    grok.context(ITask)

    def __init__(self, task):
        self.task = task

    def get_oguid(self):
        """Returns the oguid of the adapted task.
        A gouid is the client id and the intid seperated by ":".
        Example: "m1:2331"
        """

        intids = getUtility(IIntIds)
        iid = intids.getId(self.task)

        return '%s:%s' % (get_client_id(), str(iid))

    def get_indexed_data(self):
        """Returns the indexed data of the adapted task.
        """

        intids = getUtility(IIntIds)
        iid = intids.getId(self.task)

        query = getUtility(ITaskQuery)
        return query.get_task(iid, get_client_id())

    def get_predecessor(self, default=None):
        """Returns the predecessor of the adapted object or ``default`` if it
        has none or if the predecessor does not exist anymore. The
        predecessor is as a sqlachemy object (indexed data).
        """

        data = self.get_indexed_data()
        if getattr(data, 'predecessor', None):
            return data.predecessor
        else:
            return default

    def set_predecessor(self, oguid):
        """Sets the predecessor on the adapted object to ``oguid``.
        A gouid is the client id and the intid seperated by ":".
        Example: "m1:2331"
        Returns False if it failed.
        """

        client_id, iid = oguid.split(':', 1)

        # do we have it in our indexes?
        query = getUtility(ITaskQuery)
        predecessor = query.get_task(iid, client_id)
        if not predecessor:
            return False

        # set the predecessor in the task object
        self.task.predecessor = oguid
        modified(self.task)
        return True

    def get_successors(self):
        """Returns all successors of the adapted context as solr flair objects.
        """

        data = self.get_indexed_data()
        if not data:
            return None
        else:
            return data.successors

    def get_oguid_by_path(self, path, admin_unit_id):
        """Returns the oguid of another object identifed by admin_unit_id and path.
        """
        query = getUtility(ITaskQuery)
        task = query.get_task_by_path(path, admin_unit_id)
        if not task:
            return None
        else:
            return '%s:%s' % (str(task.admin_unit_id), str(task.int_id))
