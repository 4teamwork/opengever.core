from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.request import dispatch_request
from opengever.base.response import IResponseContainer
from opengever.base.transport import Transporter
from opengever.globalindex.model.task import Task
from opengever.tabbedview.helper import linked
from opengever.task import _
from opengever.task import util
from plone import api
from StringIO import StringIO
from z3c.relationfield import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import json


# XXX: This module is supposed to be temporary. The function below, as
# well as the code in opengever.task.accept.browser.utils should be moved
# to a common location.
#
# Ideally onto the Task class or a mixin for it,
# but this isn't straightforward since some of these functions operate on
# dossiers instead of tasks, or even other contexts that would need to be
# evaluated carefully before refactoring.
#
# Maybe a InterUnitSupport class with static methods to group them together
# could work. Either way, this should probably be done once the code related
# to accepting forwardings is gets wired up in API endpoints. Because
# forwardings aren't being touched in this change, moving just part of the
# code would rip apart functionality that is closely related, doing more
# harm than good.


def complete_task_and_deliver_documents(
        task, transition, docs_to_deliver=None, response_text=None,
        approved_documents=None, pass_documents_to_next_task=None):
    """Delivers the selected documents to the predecesser task and
    complete the task:

    - Copy the documents to the predecessor task (no new responses)
    - Execute workflow transition (no new response)
    - Add a new response indicating the workflow transition, the added
    documents and containing the entered response text.
    """
    # Syncing the workflow change is done during document delivery
    # (see below) therefore we skip the workflow syncing.
    transition_data = {'text': response_text}
    if approved_documents:
        transition_data['approved_documents'] = approved_documents

    if pass_documents_to_next_task:
        transition_data['pass_documents_to_next_task'] = pass_documents_to_next_task

    util.change_task_workflow_state(task,
                                    transition,
                                    disable_sync=True,
                                    **transition_data)

    response_obj = IResponseContainer(task).list()[-1]

    if docs_to_deliver is None:
        docs_to_deliver = []

    predecessor = Task.query.by_oguid(task.predecessor)

    transporter = Transporter()
    intids = getUtility(IIntIds)

    data = {'documents': [],
            'text': response_text,
            'transition': transition,
            'pass_documents_to_next_task': pass_documents_to_next_task}

    related_ids = []
    if getattr(task, 'relatedItems'):
        related_ids = [item.to_id for item in task.relatedItems]

    for doc_intid in docs_to_deliver:
        doc = intids.getObject(int(doc_intid))
        data['documents'].append(transporter.extract(doc))

        # add a releation when a document from the dossier was selected
        if int(doc_intid) not in related_ids:
            # check if its a relation
            if aq_parent(aq_inner(doc)) != task:
                # add relation to doc on task
                if task.relatedItems:
                    task.relatedItems.append(
                        RelationValue(int(doc_intid)))
                else:
                    task.relatedItems = [
                        RelationValue(int(doc_intid))]

                # add response change entry for this relation
                response_obj.add_related_item(RelationValue(int(doc_intid)))

                # set relation flag
                doc._v__is_relation = True
                response_obj.add_change(
                    'related_items',
                    '',
                    linked(doc, doc.Title()),
                    _(u'label_related_items', default=u"Related Items"))

            else:
                # add entry to the response for this document
                response_obj.added_objects.append(RelationValue(int(doc_intid)))
        else:
            # append only the relation on the response
            doc._v__is_relation = True
            response_obj.add_change(
                'related_items',
                '',
                linked(doc, doc.Title()),
                _(u'label_related_items', default=u"Related Items"))

    if api.content.get_state(task) == predecessor.review_state:
        # If the successor task is already in the same state as the predecessor
        # (e.g. both are closed), we skip changing the predecessor's state.
        #
        # This situation can occur after a conflict error during the initial
        # commit of the local transition. The transaction manager retries the
        # request, but the remote task may already have been closed and committed
        # to the OGDS. This is usually not an issue, but it's possible that
        # the current user does no longer have permission to access the predecessor
        # task, which would lead to an Unauthorized error and the local transition
        # would be aborted. Means, the predecessor remains closed, but the local
        # successor task is still open and cannot be closed anymore.
        #
        # When the retry attempts to close the local task again, we
        # detect that the predecessor is already closed as well and avoid
        # performing the transition on the remote admin unit a second time.
        #
        # Fixes https://4teamwork.atlassian.net/browse/TI-1633
        return StringIO('OK')

    request_data = {'data': json.dumps(data)}
    response = dispatch_request(
        predecessor.admin_unit_id,
        '@@complete_successor_task-receive_delivery',
        predecessor.physical_path,
        data=request_data)

    return response
