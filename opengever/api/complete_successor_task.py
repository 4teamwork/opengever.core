from opengever.api.remote_task_base import RemoteTaskBaseService
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.task.browser.complete_utils import complete_task_and_deliver_documents
from opengever.task.exceptions import TaskRemoteRequestError
from opengever.task.validators import get_checked_out_documents
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFDiffTool.utils import safe_utf8
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.intid import IIntIds


class CompleteSuccessorTaskPost(RemoteTaskBaseService):
    """Completes a successor task, its remote predecessor and optionally
    delivers back documents to the remote predecessor task.

    POST /task-42/@complete-successor-task

    {
      "transition": "task-transition-in-progress-resolved",
      "documents": [1423795951],
      "text": "I finished this task."
    }

    This endpoint will complete a successor task linked to a remote
    predecessor, by executing the given `transition` for both the local
    task (the one which this endpoint is invoked on) and the remote
    predecessor.

    Optionally, the specified `documents` from the containing dossier will be
    transported back to the remote predecessor task.
    """

    required_params = ('transition', )
    optional_params = ('documents', 'text', 'approved_documents')

    @staticmethod
    def _resolve_doc_ref_to_intid(doc_ref):
        if isinstance(doc_ref, int):
            # Already an IntId
            return doc_ref

        if isinstance(doc_ref, basestring) and '/' in doc_ref:
            # Path
            path = safe_utf8(doc_ref)
            portal = api.portal.get()
            obj = portal.restrictedTraverse(path)
            return getUtility(IIntIds).getId(obj)

        if isinstance(doc_ref, basestring) and ':' in doc_ref:
            # Oguid
            oguid = Oguid.parse(doc_ref)
            return oguid.int_id

        raise BadRequest('Unknown document reference: %r' % doc_ref)

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Extract and validate parameters, assign defaults
        params = self.extract_params()

        transition = params['transition']
        docs_to_deliver = params.get('documents', [])
        response_text = params.get('text', u'')
        approved_documents = params.get('approved_documents', [])

        # Map any supported document reference type to an IntId
        docs_to_deliver = map(self._resolve_doc_ref_to_intid, docs_to_deliver)

        invalid = get_checked_out_documents(docs_to_deliver)
        if invalid:
            raise BadRequest('Some documents are checked out.')

        # Validate that this is actually a successor task
        successor_task = self.context
        if successor_task.predecessor is None:
            raise BadRequest(
                '@complete-successor-task only supports successor tasks. '
                'This task has no predecessor.')

        # Locate predecessor, and dispatch remote request to close them
        # both, and deliver any documents if necessary
        predecessor = Task.query.by_oguid(successor_task.predecessor)
        remote_response = complete_task_and_deliver_documents(
            successor_task, transition,
            docs_to_deliver=docs_to_deliver,
            response_text=response_text,
            approved_documents=approved_documents)

        remote_response_body = remote_response.read()
        if remote_response_body.strip() != 'OK':
            raise TaskRemoteRequestError(
                'Delivering documents and updating task failed '
                'on remote client %s.' % predecessor.admin_unit_id)

        serialized_successor = self.serialize(successor_task)
        return serialized_successor
