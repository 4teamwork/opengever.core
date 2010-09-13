from opengever.base.interfaces import IOGUid
from five import grok
from opengever.globalsolr.interfaces import ISearch
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from zope.component import getUtility


class SuccessorTaskController(grok.Adapter):
    """The successor task controller manages predecessor and successor
    references between tasks.
    """

    grok.provides(ISuccessorTaskController)
    grok.context(ITask)

    def __init__(self, task):
        self.task = task

    def get_predecessor(self, default=None):
        """Returns the predecessor of the adapted object or ``default`` if it
        has none or if the predecessor does not exist anymore. The
        predecessor is returned as solr flair.
        """
        
        oguid = self.task.predecessor
        if not oguid:
            return default

        oguids = getUtility(IOGUid)
        return oguids.get_flair(oguid)

    def set_predecessor(self, oguid):
        """Sets the predecessor on the adapted object to ``oguid``.
        """
        # test if we can get flair exists
        oguids = getUtility(IOGUid)
        if not oguids.get_flair(oguid):
            return False
        # set the predecessor
        self.task.predecessor = oguid
        self.task.reindexObject()
        return True

    def get_successors(self):
        """Returns all successors of the adapted context as solr flair objects.
        """
        solr_util = getUtility(ISearch)
        oguids = getUtility(IOGUid)
        return solr_util({'predecessor': oguids.get_id(self.task)})
