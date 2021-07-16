from opengever.api.remote_task_base import RemoteTaskBaseService
from opengever.base.exceptions import MalformedOguid
from opengever.base.oguid import Oguid
from opengever.task.browser.accept.utils import accept_task_with_successor
from plone.protect.interfaces import IDisableCSRFProtection
from zExceptions import BadRequest
from zope.interface import alsoProvides


class AcceptRemoteTaskPost(RemoteTaskBaseService):
    """Accepts a task on a remote admin unit by creating a successor copy
    in the dossier the endpoint was invoked on.

    POST /dossier-17/@accept-remote-task

    {
      "task_oguid": "fd:12345",
      "text": "I'm accepting this task into this dossier."
    }

    This endpoint will accept a remote task (a task that is assigned to the
    current user, but physically is located on a different admin unit) by
    creating a successor copy in the local dossier, and linking the successor
    task with its predecessor on the remote admin unit.

    Documents attached to the remote task get copied to the local task copy
    as well.

    The remote task is identified via the "task_oguid" in the JSON body, and
    *must* be on a different admin unit than the current one.
    """

    required_params = ('task_oguid', )
    optional_params = ('text', )

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Extract and validate parameters, assign defaults
        params = self.extract_params()

        raw_task_oguid = params['task_oguid']
        response_text = params.get('text', u'')

        # Validate that Oguid is well-formed and refers to a task that is
        # actually remote. Turn any Python exceptions into proper
        # 400 Bad Request responses with details in the JSON body.
        try:
            task_oguid = Oguid.parse(raw_task_oguid)
        except MalformedOguid as exc:
            raise BadRequest(self.format_exception(exc))

        if not self.is_remote(task_oguid):
            raise BadRequest(
                'Task must be on remote admin unit. '
                'Oguid %s refers to a local task, however.' % raw_task_oguid)

        # dispatch remote request to accept task in given dossier,
        # creating a copy of the task and its attached documents
        dossier_to_accept_in = self.context
        successor = accept_task_with_successor(
            dossier_to_accept_in,
            raw_task_oguid,
            response_text,
        )

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", successor.absolute_url())

        serialized_successor = self.serialize(successor)
        return serialized_successor
