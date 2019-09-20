from opengever.base.request import dispatch_request
from opengever.base.request import tracebackify
from opengever.base.utils import ok_response
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.base.response import IResponseContainer
from opengever.task.interfaces import IResponseSyncerSender
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.util import add_simple_response
from Products.CMFDiffTool.utils import safe_utf8
from Products.Five import BrowserView
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.interface import implements
import AccessControl


class ResponseSyncerSenderException(Exception):
    """An exception raised if something went wrong while syncing
    the response-object.
    """


def sync_task_response(task, request, syncer_name, transition, text, **kwargs):
    """Method to get the responsible IResponseSyncerSender adapter
    and run the response syncing process for predecessors and successors
    of the current task.

    :param task: An object providing the ITask interface
    :param request: The current request
    :param syncer_name: A name of a IResponseSyncerSender adapter name
    :param transition: The transition which has been done and should be synced now.
    :param text: The response text.
    :param kwargs: additional arguments for sending to the receiver
    """
    syncer = getMultiAdapter(
        (task, request), IResponseSyncerSender, name=syncer_name)

    return syncer.sync_related_tasks(transition, text, **kwargs)


class BaseResponseSyncerSender(object):
    """Abstract ResponseSyncerSender base class for performing a task sync between
    admin-units. This class is responsible for sending the data to other admin-units
    """
    implements(IResponseSyncerSender)

    TARGET_SYNC_VIEW_NAME = None  # Nedds to be defined in a subclass

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sync_related_tasks(self, transition, text, **kwargs):
        tasks = self.get_related_tasks_to_sync(transition)
        for task in tasks:
            self.sync_related_task(task, transition, text, **kwargs)

        return tasks

    def get_related_tasks_to_sync(self, transition=''):
        tasks = []
        stc = ISuccessorTaskController(self.context)
        predecessor = stc.get_predecessor(None)
        if predecessor:
            tasks.append(predecessor)

        tasks.extend(stc.get_successors())

        return tasks

    def sync_related_task(self, task, transition, text, **kwargs):
        payload = {'transition': transition,
                   'text': safe_utf8(text or '')}
        self.extend_payload(payload, task, **kwargs)

        response = self._dispatch_request(
            task.admin_unit_id,
            self.TARGET_SYNC_VIEW_NAME,
            task.physical_path,
            data=payload)

        response_data = response.read().strip()
        if response_data != 'OK':
            self.raise_sync_exception(task, transition, text, **kwargs)

    def extend_payload(self, payload, task, **kwargs):
        payload.update(kwargs)

    def raise_sync_exception(self, task, transition, text, **kwargs):
        raise ResponseSyncerSenderException()

    def _dispatch_request(self, target_admin_unit_id, viewname, path, data):
        return dispatch_request(target_admin_unit_id, viewname, path, data)


@tracebackify(to_re_raise=Forbidden)
class BaseResponseSyncerReceiver(BrowserView):
    """Abstract ResponseSyncerReceiver view for receiving requests from a
    ResponseSyncerSender and updates the current task with the received data

    The view returns "OK" if everything went fine.
    The view will raise a Forbidden-Exception if the user is not allowed to use
    this view.
    """

    def __call__(self):
        self._check_internal_request()

        transition = self.request.get('transition')
        text = self.request.get('text')

        if self._is_already_done(transition, text):
            return ok_response(self.request)

        self._update(transition, text)
        return ok_response(self.request)

    def _update(self, transition, text):
        """Updates the current task with the received data
        """
        return add_simple_response(self.context, transition=transition, text=text)

    def _check_internal_request(self):
        # WARNING: The security is done here by using the request layer
        # IInternalOpengeverRequestLayer provided by the ogds PAS plugin.
        # The view has to be public, since the user may not have any
        # permission on this context.
        if not IInternalOpengeverRequestLayer.providedBy(self.request):
            raise Forbidden()

    def _is_already_done(self, transition, text):
        """This method returns `True` if this exact request was already
        executed.
        This is the case when the sender client has a conflict error when
        committing and the sender-request needs to be re-done. In this case
        this view is called another time but the changes were already made
        and committed - so we need to return "OK" and do nothing.
        """
        response_container = IResponseContainer(self.context)
        if len(response_container) == 0:
            return False

        last_response = response_container.list()[-1]
        current_user = AccessControl.getSecurityManager().getUser()

        if last_response.transition == transition and \
                last_response.creator == current_user.getId() and \
                last_response.text == text:
            return True

        else:
            return False
