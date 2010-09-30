from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from sqlalchemy.orm.exc import NoResultFound


class QueryTask(object):
    """
    """
    
    def __init__(self):
        self.session = Session()
    
    def get_task(self, int_id, client_id):
        """
        """
        try:
            task = self.session.query(Task).filter(Task.client_id==client_id).filter(
                Task.int_id==int_id).one()
        except NoResultFound:
            task = None
        return task
    
    def get_tasks_for_responsible(self, responsible):
        """
        """
        return self.session.query(Task).filter(Task.responsible==responsible).all()
    
    def get_tasks_for_issuer(self, issuer):
        """
        """
