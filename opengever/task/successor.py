from five import grok
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
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
        """Returns the oguid of the adapted task."""

        return self.task.oguid.id

    def get_predecessor(self, default=None):
        """Returns the predecessor of the adapted object or ``default`` if it
        has none or if the predecessor does not exist anymore. The
        predecessor is as a sqlachemy object (indexed data).
        """

        sqltask = self.task.get_sql_object()
        if getattr(sqltask, 'predecessor', None):
            return sqltask.predecessor
        else:
            return default

    def set_predecessor(self, oguid):
        """Sets the predecessor on the adapted object to ``oguid``.
        A gouid is the client id and the intid seperated by ":".
        Example: "m1:2331"
        Returns False if it failed.
        """

        oguid = Oguid(oguid=oguid)

        # do we have it in our indexes?
        predecessor = Task.query.by_oguid(oguid)
        if not predecessor:
            return False

        # set the predecessor in the task object
        self.task.predecessor = oguid.id
        modified(self.task)
        return True

    def get_successors(self):
        """Returns all successors of the adapted context as solr flair objects.
        """

        sqltask = self.task.get_sql_object()
        if not sqltask:
            return None
        else:
            return sqltask.successors

    def get_oguid_by_path(self, path, admin_unit_id):
        """Returns the oguid of another object identifed by admin_unit_id and path.
        """
        task = Task.query.by_path(path, admin_unit_id)
        if not task:
            return None
        return task.oguid.id
