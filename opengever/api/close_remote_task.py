from opengever.api.remote_task_base import RemoteTaskBaseService
from opengever.base.exceptions import MalformedOguid
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.task.browser.close import CloseTaskHelper
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from zExceptions import BadRequest
from zope.interface import alsoProvides


class CloseRemoteTaskPost(RemoteTaskBaseService):
    """Close a task on a remote admin unit, copying documents to the given
    dossier on the current admin unit if selected.

    this is only possible for `information`-tasks

    POST /dossier-17/@close-remote-task

    {
      "task_oguid": "fd:12345",
      "text": "I'm accepting this task into this dossier."
      "dossier_uid": "9823u409823094"
      "document_oguids": ["rk:23459", "rk:94598"]
    }

    This endpoint will close a remote task (a task that is assigned to the
    current user, but physically is located on a different admin unit) and
    copy the selected documents to the given dossier.

    The remote task is identified via the "task_oguid" in the JSON body, and
    *must* be on a different admin unit than the current one.
    """

    required_params = ('task_oguid', )
    optional_params = ('text', 'document_oguids', 'dossier_uid')

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Extract and validate parameters, assign defaults
        params = self.extract_params()

        raw_task_oguid = params['task_oguid']
        response_text = params.get('text', u'')
        dossier_uid = params.get('dossier_uid', u'')
        document_oguids = params.get('document_oguids', u'')

        # Validate that Oguid is well-formed and refers to a task that is
        # actually remote. Turn any Python exceptions into proper
        # 400 Bad Request responses with details in the JSON body.
        try:
            task_oguid = Oguid.parse(raw_task_oguid)
            task = Task.query.by_oguid(task_oguid)
        except MalformedOguid as exc:
            raise BadRequest(self.format_exception(exc))

        if document_oguids and not dossier_uid:
            raise BadRequest('dossier_uid is required when selecting '
                             'documents for copying.')

        if not self.is_remote(task_oguid):
            raise BadRequest(
                'Task must be on remote admin unit. '
                'Oguid %s refers to a local task, however.' % raw_task_oguid)

        closer = CloseTaskHelper()
        dossier = None
        if dossier_uid:
            dossier = uuidToObject(dossier_uid)
            document_intids = [Oguid.parse(oguid).int_id for oguid in document_oguids]
            closer.copy_documents(task, dossier, document_intids)

        closer.close_task(task, response_text)

        if dossier:
            self.request.response.setStatus(201)
            self.request.response.setHeader("Location", dossier.absolute_url())

            serialized_dossier = self.serialize(dossier)
            return serialized_dossier

        self.request.response.setStatus(204)
