from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.task.browser.complete_utils import complete_task_and_deliver_documents
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFDiffTool.utils import safe_utf8
from zExceptions import BadRequest
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.intid import IIntIds
import json


class CompleteSuccessorTaskPost(Service):
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

    def _format_exception(self, exc):
        return '%s: %s' % (exc.__class__.__name__, str(exc))

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

        # Extract and validate parameters
        json_data = json_body(self.request)

        transition = json_data.pop('transition', None)
        if not transition:
            raise BadRequest(
                'Required parameter "transition" is missing in body')

        docs_to_deliver = json_data.pop('documents', [])
        response_text = json_data.pop('text', u'')

        # Reject any unexpected parameters
        unexpected_params = json_data.keys()
        if unexpected_params:
            raise BadRequest(
                'Unexpected parameter(s) in JSON '
                'body: %s. Supported parameters are: '
                '["transition", "documents", "text"]'
                % json.dumps(unexpected_params))

        # Map any supported document reference type to an IntId
        docs_to_deliver = map(self._resolve_doc_ref_to_intid, docs_to_deliver)

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
            response_text=response_text)

        remote_response_body = remote_response.read()
        if remote_response_body.strip() != 'OK':
            raise Exception('Delivering documents and updating task failed '
                            'on remote client %s.' % predecessor.admin_unit_id)

        serializer = queryMultiAdapter(
            (successor_task, self.request), ISerializeToJson)
        serialized_successor = serializer()
        serialized_successor["@id"] = successor_task.absolute_url()
        return serialized_successor
