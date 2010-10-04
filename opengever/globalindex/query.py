from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implements
from opengever.globalindex.interfaces import ITaskQuery

class TaskQuery(object):
    """A global utility for querying opengever tasks.
    """
    implements(ITaskQuery)

    def get_task(self, int_id, client_id):
        """Returns the task identified by the given int_id and client_id.
        """
        try:
            task = Session().query(Task).filter(Task.client_id==client_id).filter(
                Task.int_id==int_id).one()
        except NoResultFound:
            task = None
        return task

    def get_tasks_for_responsible(self, responsible):
        """Returns all tasks assigned to the given responsible.
        """
        return Session().query(Task).filter(Task.responsible==responsible).all()

    def get_tasks_for_issuer(self, issuer):
        """Returns all tasks issued by the given issuer.
        """
        return Session().query(Task).filter(Task.issuer==issuer).all()
