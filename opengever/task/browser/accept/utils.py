from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request, get_client_id
from opengever.task import _
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import CustomInitialVersionMessage
from opengever.task.util import change_task_workflow_state
from plone.dexterity.utils import createContentInContainer
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.i18n import translate
import AccessControl
import transaction


# TODO: The whole yearfolder functionality should be moved to opengever.inbox

ACCEPT_TASK_TRANSITION = 'task-transition-open-in-progress'


def _get_yearfolder(inbox):
    """Returns the yearfolder for the current year (creates it if missing).
    """

    year = str(datetime.now().year)
    if inbox.get(year):
        return inbox.get(year)
    else:
        return _create_yearfolder(inbox, year)


def _create_yearfolder(inbox, year):
    """creates the yearfolder for the given year"""

    _sm = AccessControl.getSecurityManager()
    AccessControl.SecurityManagement.newSecurityManager(
        inbox.REQUEST,
        AccessControl.SecurityManagement.SpecialUsers.system)
    try:
        # for creating the folder, we need to be a superuser since
        # normal user should not be able to add year folders.
        # --- help i18ndude ---
        msg = _(u'yearfolder_title', default=u'Closed ${year}',
                mapping=dict(year=str(year)))
        # --- / help i18ndude ---
        folder_title = translate(str(msg), msg.domain, msg.mapping,
                                 context=inbox.REQUEST, default=msg.default)
        folder = createContentInContainer(
            inbox, 'opengever.inbox.yearfolder',
            title=folder_title, id=year)
    except:
        AccessControl.SecurityManagement.setSecurityManager(_sm)
        raise
    else:
        AccessControl.SecurityManagement.setSecurityManager(_sm)

    return folder


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
    predecessor = getUtility(ITaskQuery).get_task_by_oguid(predecessor_oguid)

    # get the inbox
    cat = getToolByName(context, 'portal_catalog')
    inboxes = cat(portal_type="opengever.inbox.inbox")

    if len(inboxes) == 0:
        raise Unauthorized()
    else:
        inbox = inboxes[0].getObject()

    # transport the remote forwarding to the inbox or actual yearfolder
    transporter = getUtility(ITransporter)
    if dossier:
        yearfolder = _get_yearfolder(inbox, )
        successor_forwarding = transporter.transport_from(
            yearfolder, predecessor.admin_unit_id, predecessor.physical_path)
    else:
        successor_forwarding = transporter.transport_from(
            inbox, predecessor.admin_unit_id, predecessor.physical_path)

    # Replace the issuer with the current inbox
    successor_forwarding.issuer = u'inbox:%s' % get_client_id()

    # Set the "X-CREATING-SUCCESSOR" flag for preventing the event handler
    # from creating additional responses per added document.
    successor_forwarding.REQUEST.set('X-CREATING-SUCCESSOR', True)

    successor_tc = ISuccessorTaskController(successor_forwarding)

    # copy documents and map the intids
    doc_transporter = getUtility(ITaskDocumentsTransporter)
    with CustomInitialVersionMessage(
        _(u'version_message_accept_forwarding',
          default=u'Document copied from forwarding (forwarding accepted)'),
        context.REQUEST):
        intids_mapping = doc_transporter.copy_documents_from_remote_task(
            predecessor, successor_forwarding)

    # copy the responses
    response_transporter = IResponseTransporter(successor_forwarding)
    response_transporter.get_responses(predecessor.admin_unit_id,
                                       predecessor.physical_path,
                                       intids_mapping=intids_mapping)

    # if a dossier is given means that a successor task must
    # be created in a new or a existing dossier
    if dossier:
        # we need all task field values from the forwarding
        fielddata = {}
        for fieldname in ITask.names():
            value = ITask.get(fieldname).get(successor_forwarding)
            fielddata[fieldname] = value

        # lets create a new task - the successor task
        task = createContentInContainer(
            dossier, 'opengever.task.task', **fielddata)

        # copy documents and map the intids

        intids_mapping = _copy_documents_from_forwarding(
            successor_forwarding, task)

        # copy the responses
        response_transporter = IResponseTransporter(task)
        response_transporter.get_responses(
            get_client_id(),
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

    response = remote_request(predecessor.client_id,
                              '@@store_forwarding_in_yearfolder',
                              path=predecessor.physical_path,
                              data=request_data)

    if response.read().strip() != 'OK':
        raise Exception('Adding the response and changing the '
                        'workflow state on the predecessor forwarding '
                        'failed.')

    if dossier:
        # when a successor task exists, we close also the successor forwarding
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


def assign_forwarding_to_dossier(
    context, forwarding_oguid, dossier, response_text):

    forwarding = getUtility(ITaskQuery).get_task_by_oguid(forwarding_oguid)

    forwarding_obj = context.unrestrictedTraverse(
        forwarding.physical_path.encode('utf-8'))

    # we need all task field values from the forwarding
    fielddata = {}
    for fieldname in ITask.names():
        value = ITask.get(fieldname).get(forwarding_obj)
        fielddata[fieldname] = value

    # lets create a new task - the successor task
    task = createContentInContainer(
        dossier, 'opengever.task.task', **fielddata)

    successor_tc_task = ISuccessorTaskController(task)

    # copy documents and map the intids
    intids_mapping = _copy_documents_from_forwarding(forwarding_obj, task)

    # copy the responses
    response_transporter = IResponseTransporter(task)
    response_transporter.get_responses(
        get_client_id(),
        '/'.join(forwarding_obj.getPhysicalPath()),
        intids_mapping=intids_mapping)

    # close and store the forwarding in yearfolder
    change_task_workflow_state(
        forwarding_obj,
        'forwarding-transition-assign-to-dossier',
        text=response_text,
        successor_oguid=successor_tc_task.get_oguid())

    inbox = aq_parent(aq_inner(forwarding_obj))
    yearfolder = _get_yearfolder(inbox)
    clipboard = inbox.manage_cutObjects((forwarding_obj.getId(),))
    yearfolder.manage_pasteObjects(clipboard)

    # successor
    successor_tc_task.set_predecessor(forwarding_oguid)

    return task


def accept_task_with_successor(dossier, predecessor_oguid, response_text):

    predecessor = getUtility(ITaskQuery).get_task_by_oguid(predecessor_oguid)

    # Transport the original task (predecessor) to this dossier. The new
    # response and task change is not yet done and will be done later. This
    # is necessary for beeing as transaction aware as possible.
    transporter = getUtility(ITransporter)
    successor = transporter.transport_from(
        dossier, predecessor.client_id, predecessor.physical_path)
    successor_tc = ISuccessorTaskController(successor)

    # Set the "X-CREATING-SUCCESSOR" flag for preventing the event handler
    # from creating additional responses per added document.
    successor.REQUEST.set('X-CREATING-SUCCESSOR', True)

    # copy documents and map the intids
    doc_transporter = getUtility(ITaskDocumentsTransporter)
    with CustomInitialVersionMessage(
        _(u'version_message_accept_task',
          default=u'Document copied from task (task accepted)'),
        dossier.REQUEST):
        intids_mapping = doc_transporter.copy_documents_from_remote_task(
            predecessor, successor)

    # copy the responses
    response_transporter = IResponseTransporter(successor)
    response_transporter.get_responses(predecessor.admin_unit_id,
                                       predecessor.physical_path,
                                       intids_mapping=intids_mapping)

    # First "accept" the successor task..
    accept_task_with_response(successor, response_text)

    transaction.savepoint()
    response_text = response_text or ''
    request_data = {'text': response_text.encode('utf-8'),
                    'successor_oguid': successor_tc.get_oguid()}

    response = remote_request(predecessor.client_id,
                              '@@accept_task_workflow_transition',
                              path=predecessor.physical_path,
                              data=request_data)

    if response.read().strip() != 'OK':
        raise Exception('Adding the response and changing the '
                        'workflow state on the predecessor task '
                        'failed.')

    # Connect the predecessor and the successor task. This needs to be done
    # that late for preventing a deadlock because of the locked tasks table.
    successor_tc.set_predecessor(predecessor_oguid)

    return successor


class AcceptTaskWorkflowTransitionView(grok.View):
    grok.context(ITask)
    grok.name('accept_task_workflow_transition')
    grok.require('cmf.AddPortalContent')

    def render(self):

        # Set correct content type for text response
        self.request.response.setHeader("Content-type", "tex/plain")

        if self.is_already_accepted():
            return 'OK'

        text = self.request.get('text')
        successor_oguid = self.request.get('successor_oguid')

        accept_task_with_response(self.context, text,
                                  successor_oguid=successor_oguid)
        return 'OK'

    def is_already_accepted(self):
        """When the sender has a conflict error but the reseiver already
        added the response, this view is called a second / third time in
        conflict resolution. We need to detect whether it is already done
        and not fail.
        """

        response_container = IResponseContainer(self.context)
        if len(response_container) == 0:
            return False

        last_response = response_container[-1]
        current_user = AccessControl.getSecurityManager().getUser()

        if last_response.transition == ACCEPT_TASK_TRANSITION and \
                last_response.creator == current_user.getId():
            return True

        else:
            return False
