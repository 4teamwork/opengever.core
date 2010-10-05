from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import asc, desc
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

    def get_tasks_for_responsible(self, responsible, sort_on='modified', sort_order='reverse'):
        """Returns all tasks assigned to the given responsible.
        """
        sort_on = getattr(Task, sort_on)
        if sort_order == 'reverse':
            return Session().query(Task).filter(Task.responsible==responsible
                ).order_by(desc(sort_on)).all()
        else:
            return Session().query(Task).filter(Task.responsible==responsible
                ).order_by(asc(sort_on)).all()

    def get_tasks_for_issuer(self, issuer, sort_on='modified', sort_order='reverse'):
        """Returns all tasks issued by the given issuer.
        """
        sort_on = getattr(Task, sort_on)
        if sort_order == 'reverse':
            return Session().query(Task).filter(Task.issuer==issuer
                ).order_by(desc(sort_on)).all()
        else:
            return Session().query(Task).filter(Task.issuer==issuer
                ).order_by(asc(sort_on)).all()

    def get_task_for_assigned_client(self, client, sort_on='modified', sort_order='reverse'):
        """Return all task assigned to the actual client.
        """
        sort_on = getattr(Task, sort_on)
        if sort_order == 'reverse':
            return Session().query(Task).filter(Task.assigned_client==client
                ).order_by(desc(sort_on)).all()
        else:
            return Session().query(Task).filter(Task.assigned_client==client
                ).order_by(asc(sort_on)).all()
