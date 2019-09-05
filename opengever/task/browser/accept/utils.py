from opengever.activity import notification_center
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_request
from opengever.base.request import tracebackify
from opengever.base.transport import Transporter
from opengever.base.utils import ok_response
from opengever.globalindex.model.task import Task
from opengever.inbox.utils import get_current_inbox
from opengever.inbox.yearfolder import get_current_yearfolder
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import _
from opengever.base.response import IResponseContainer
from opengever.task.exceptions import TaskRemoteRequestError
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.reminder.reminder import TaskReminder
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import change_task_workflow_state
from plone.dexterity.utils import createContentInContainer
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.globalrequest import getRequest
import AccessControl
import transaction


# TODO: The whole yearfolder functionality should be moved to opengever.inbox

ACCEPT_TASK_TRANSITION = 'task-transition-open-in-progress'

# default task type for successor tasks of a forwarding
FORWARDING_SUCCESSOR_TYPE = u'information'


def _copy_documents_from_forwarding(from_obj, to_obj):
    # set prevent copyname key on the request
    from_obj.REQUEST['prevent-copyname-on-document-copy'] = True

    intids_mapping = {}
    intids = getUtility(IIntIds)

    objs = from_obj.getFolderContents(full_objects=True,)

    for obj in objs:
        clipboard = from_obj.manage_copyObjects([obj.id, ])
        new_ids = to_obj.manage_pasteObjects(clipboard)
        intids_mapping[intids.getId(obj)] = intids.getId(
            to_obj.get(new_ids[0].get('id')))

    return intids_mapping


def accept_task_with_response(task, response_text, successor_oguid=None):
    transition = ACCEPT_TASK_TRANSITION
    response = change_task_workflow_state(task,
                                          transition,
                                          text=response_text,
                                          successor_oguid=successor_oguid)
    return response


def accept_forwarding_with_successor(
    context, predecessor_oguid, response_text, dossier=None):

    # the predessecor (the forwarding on the remote client)
    predecessor = Task.query.by_oguid(predecessor_oguid)

    # Set the "X-CREATING-SUCCESSOR" flag for preventing the event handler
    # from creating additional responses per added document.
    context.REQUEST.set('X-CREATING-SUCCESSOR', True)

    # transport the remote forwarding to the inbox or actual yearfolder
    transporter = Transporter()
    inbox = get_current_inbox(context)
    if dossier:
        yearfolder = get_current_yearfolder(inbox=inbox)
        successor_forwarding = transporter.transport_from(
            yearfolder, predecessor.admin_unit_id, predecessor.physical_path)
    else:
        successor_forwarding = transporter.transport_from(
            inbox, predecessor.admin_unit_id, predecessor.physical_path)

    # Replace the issuer with the current inbox
    successor_forwarding.issuer = get_current_org_unit().inbox().id()

    successor_tc = ISuccessorTaskController(successor_forwarding)

    # copy documents and map the intids
    doc_transporter = getUtility(ITaskDocumentsTransporter)

    comment = _(
        u'version_message_accept_forwarding',
        default=u'Document copied from forwarding (forwarding accepted)')
    intids_mapping = doc_transporter.copy_documents_from_remote_task(
        predecessor, successor_forwarding, comment=comment)

    # copy the responses
    response_transporter = IResponseTransporter(successor_forwarding)
    response_transporter.get_responses(predecessor.admin_unit_id,
                                       predecessor.physical_path,
                                       intids_mapping=intids_mapping)

    # Remove current responsible from predecessor and add issuer
    # and responsible to successor's watcher.
    center = notification_center()
    center.remove_task_responsible(Oguid.parse(predecessor_oguid),
                                   successor_forwarding.responsible)
    center.add_task_responsible(successor_forwarding,
                                successor_forwarding.responsible)
    center.add_task_issuer(successor_forwarding, successor_forwarding.issuer)

    # if a dossier is given means that a successor task must
    # be created in a new or a existing dossier
    if dossier:
        # we need all task field values from the forwarding
        fielddata = {}
        for fieldname in ITask.names():
            value = ITask.get(fieldname).get(successor_forwarding)
            fielddata[fieldname] = value

        # Predefine the task_type to avoid tasks with an invalid task_type
        fielddata['task_type'] = FORWARDING_SUCCESSOR_TYPE

        # lets create a new task - the successor task
        task = createContentInContainer(
            dossier, 'opengever.task.task', **fielddata)

        # copy documents and map the intids
        intids_mapping = _copy_documents_from_forwarding(
            successor_forwarding, task)

        # copy the responses
        response_transporter = IResponseTransporter(task)
        response_transporter.get_responses(
            get_current_admin_unit().id(),
            '/'.join(successor_forwarding.getPhysicalPath()),
            intids_mapping=intids_mapping)

        # successor
        successor_tc_task = ISuccessorTaskController(task)

    transaction.savepoint()

    # Close the predessecor forwarding
    response_text = response_text or ''
    request_data = {'response_text': response_text.encode('utf-8'),
                    'successor_oguid': successor_tc.get_oguid(),
                    'transition': 'forwarding-transition-accept'}

    response = dispatch_request(predecessor.admin_unit_id,
                                '@@store_forwarding_in_yearfolder',
                                path=predecessor.physical_path,
                                data=request_data)

    response_body = response.read()
    if response_body.strip() != 'OK':
        raise TaskRemoteRequestError(
            'Adding the response and changing the workflow state on the '
            'predecessor forwarding failed.')

    if dossier:
        # Update watchers for created successor forwarding and task
        center = notification_center()
        center.remove_task_responsible(successor_forwarding, task.responsible)
        center.add_task_responsible(task, task.responsible)

        # When a successor task exists, we close also the successor forwarding
        change_task_workflow_state(
            successor_forwarding,
            'forwarding-transition-accept',
            text=response_text,
            successor_oguid=successor_tc_task.get_oguid())

    # create the succssor relations
    successor_tc.set_predecessor(predecessor_oguid)
    if dossier:
        successor_tc_task.set_predecessor(successor_tc.get_oguid())
        return task
    return successor_forwarding


def accept_task_with_successor(dossier, predecessor_oguid, response_text):
    predecessor = Task.query.by_oguid(predecessor_oguid)

    # Set the "X-CREATING-SUCCESSOR" flag for preventing the event handler
    # from creating additional responses per added document.
    getRequest().set('X-CREATING-SUCCESSOR', True)

    # Transport the original task (predecessor) to this dossier. The new
    # response and task change is not yet done and will be done later. This
    # is necessary for beeing as transaction aware as possible.
    transporter = Transporter()
    successor = transporter.transport_from(
        dossier, predecessor.admin_unit_id, predecessor.physical_path)
    successor_tc = ISuccessorTaskController(successor)

    # copy documents and map the intids
    doc_transporter = getUtility(ITaskDocumentsTransporter)

    comment = _(u'version_message_accept_task',
               default=u'Document copied from task (task accepted)')
    intids_mapping = doc_transporter.copy_documents_from_remote_task(
        predecessor, successor, comment=comment)

    # copy the responses
    response_transporter = IResponseTransporter(successor)
    response_transporter.get_responses(predecessor.admin_unit_id,
                                       predecessor.physical_path,
                                       intids_mapping=intids_mapping)

    # Move current responsible from predecessor task to successor
    center = notification_center()
    center.add_task_responsible(successor, successor.responsible)

    # First "accept" the successor task..
    accept_task_with_response(successor, response_text)

    transaction.savepoint()
    response_text = response_text or ''
    request_data = {'text': response_text.encode('utf-8'),
                    'successor_oguid': successor_tc.get_oguid()}

    response = dispatch_request(predecessor.admin_unit_id,
                                '@@accept_task_workflow_transition',
                                path=predecessor.physical_path,
                                data=request_data)

    response_body = response.read()
    if response_body.strip() != 'OK':
        raise TaskRemoteRequestError(
            'Adding the response and changing the workflow state on the '
            'predecessor task failed.')

    # Connect the predecessor and the successor task. This needs to be done
    # that late for preventing a deadlock because of the locked tasks table.
    successor_tc.set_predecessor(predecessor_oguid)

    return successor


@tracebackify
class AcceptTaskWorkflowTransitionView(BrowserView):
    """A remote request view called by another adminunit, to accept a task,
    during the SuccessorTask creation process.

    Additionally to workflow state change, it removes the task's responsible
    from the notification_center's watcher list. Because the responsible of
    the task will watch the successor.
    """

    def __call__(self):
        if self.is_already_accepted():
            return ok_response()

        text = safe_unicode(self.request.get('text'))
        successor_oguid = self.request.get('successor_oguid')

        center = notification_center()
        center.remove_task_responsible(self.context, self.context.responsible)

        # Remove task reminders of potential responsibles
        reminders = TaskReminder().get_reminders_of_potential_responsibles(self.context)
        for userid in reminders.keys():
            TaskReminder().clear_reminder(self.context, user_id=userid)

        accept_task_with_response(self.context, text,
                                  successor_oguid=successor_oguid)
        return ok_response()

    def is_already_accepted(self):
        """When the sender has a conflict error but the reseiver already
        added the response, this view is called a second / third time in
        conflict resolution. We need to detect whether it is already done
        and not fail.
        """

        response_container = IResponseContainer(self.context)
        if len(response_container) == 0:
            return False

        last_response = response_container.list()[-1]
        current_user = AccessControl.getSecurityManager().getUser()

        if last_response.transition == ACCEPT_TASK_TRANSITION and \
                last_response.creator == current_user.getId():
            return True

        else:
            return False
