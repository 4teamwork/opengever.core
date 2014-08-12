from opengever.globalindex import Session
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.globalindex.oguid import Oguid
from sqlalchemy.sql.expression import asc, desc
from zope.deprecation import deprecated
from zope.interface import implements


class TaskQuery(object):
    """A global utility for querying opengever tasks.
    """
    implements(ITaskQuery)

    def get_tasks_for_client(self, client, sort_on='modified'):
        """Return a sqlachemy query of all task on the specified client.
        """

        sort_on = getattr(Task, sort_on)
        return Session().query(Task).filter(Task.client_id == client
                                            ).order_by(asc(sort_on)).all()
