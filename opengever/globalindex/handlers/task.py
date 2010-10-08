from AccessControl.PermissionRole import rolesForPermissionOn
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _mergedLocalRoles
from datetime import datetime
from opengever.base.interfaces import ISequenceNumber
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_client_id
from sqlalchemy.orm.exc import NoResultFound
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


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

    # we need to have python datetime objects for make it work with sqlite etc.
    try:
        task.deadline = datetime(obj.deadline)
    except TypeError:
        pass
    try:
        task.completed = datetime(obj.date_of_completion)
    except TypeError:
        pass
    try:
        task.modified = datetime(obj.modified())
    except TypeError:
        pass

    task.task_type = obj.task_type
    task.sequence_number = getUtility(ISequenceNumber).get_number(obj)

    task.assigned_client = obj.responsible_client

    # index the predecessor
    if obj.predecessor:
        pred_client_id, pred_init_id = obj.predecessor.split(':', 1)
        predecessor = session.query(Task).filter_by(client_id=pred_client_id,
                                                    int_id=pred_init_id).one()
    else:
        predecessor = None

    task.predecessor = predecessor

    # index the principal which have View permission. This is according to the
    # allowedRolesAndUsers index but it does not car of global roles.
    allowed_roles = rolesForPermissionOn(View, obj)
    principals = []
    for principal, roles in _mergedLocalRoles(obj).items():
        for role in roles:
            if role in allowed_roles:
                principals.append(principal.decode('utf-8'))
                break

    task.principals = principals
