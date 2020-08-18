from opengever.base.exceptions import MalformedOguid
from opengever.base.oguid import Oguid
from opengever.task.browser.accept.utils import accept_task_with_successor
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
import json


class AcceptRemoteTaskPost(Service):
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

    def _format_exception(self, exc):
        return '%s: %s' % (exc.__class__.__name__, str(exc))

    def is_remote(self, oguid):
        return not oguid.is_on_current_admin_unit

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Extract and validate parameters
        json_data = json_body(self.request)

        raw_task_oguid = json_data.pop('task_oguid', None)
        if not raw_task_oguid:
            raise BadRequest(
                'Required parameter "task_oguid" is missing in body')

        response_text = json_data.pop('text', u'')

        # Reject any unexpected parameters
        unexpected_params = json_data.keys()
        if unexpected_params:
            raise BadRequest(
                'Unexpected parameter(s) in JSON '
                'body: %s. Supported parameters are: '
                '["task_oguid", "text"]' % json.dumps(unexpected_params))

        # Validate that Oguid is well-formed and refers to a task that is
        # actually remote. Turn any Python exceptions into proper
        # 400 Bad Request responses with details in the JSON body.
        try:
            task_oguid = Oguid.parse(raw_task_oguid)
        except MalformedOguid as exc:
            raise BadRequest(self._format_exception(exc))

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

        serializer = queryMultiAdapter((successor, self.request), ISerializeToJson)
        serialized_successor = serializer()
        serialized_successor["@id"] = successor.absolute_url()
        return serialized_successor
