from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_client_id
from opengever.task.task import assigned_client
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from sqlalchemy.orm.exc import NoResultFound


def index_task(obj, event):
    """Index the given task in opengever.globalindex.
    """
    client_id = get_client_id()
    intids = getUtility(IIntIds)
    int_id = intids.getId(obj)
    session = Session()
    try:
        task = session.query(Task).filter(Task.client_id==client_id).filter(
            Task.int_id==int_id).one()
    except NoResultFound:
        task = Task(int_id, client_id)
        session.add(task)

    task.title = obj.title
    url_tool = obj.unrestrictedTraverse('@@plone_tools').url()
    task.physical_path = '/'.join(url_tool.getRelativeContentPath(obj))
    task.review_state = obj.unrestrictedTraverse('@@plone_context_state').workflow_state()
    task.icon = obj.getIcon()
    task.responsible = obj.responsible
    task.issuer = obj.issuer
    task.deadline = obj.deadline
    task.completed = obj.date_of_completion
    task.modified = obj.modified()

    task.task_type = obj.task_type
    task.sequence_number = obj.sequence_number

    task.assigned_client = obj.responsible_client
    # index the predecessor
    if obj.predecessor:
        pred_client_id, pred_init_id = obj.predecessor.split(':', 1)
        predecessor = session.query(Task).filter_by(client_id=pred_client_id,
                                                    int_id=pred_init_id).one()
    else:
        predecessor = None

    task.predecessor = predecessor

