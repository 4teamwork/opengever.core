from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import encode_after_json
from opengever.ogds.base.utils import remote_json_request
from opengever.ogds.base.utils import remote_request
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from zope.component import getUtility
import json
import transaction


def accept_task_with_response(task, response_text, successor_oguid=None):
    transition = 'task-transition-open-in-progress'
    wftool = getToolByName(task, 'portal_workflow')

    before = wftool.getInfoFor(task, 'review_state')
    before = wftool.getTitleForStateOnType(before, task.Type())

    wftool.doActionFor(task, transition)

    after = wftool.getInfoFor(task, 'review_state')
    after = wftool.getTitleForStateOnType(after, task.Type())

    response = add_simple_response(task, text=response_text,
                                   successor_oguid=successor_oguid)
    response.add_change('review_state', _(u'Issue state'),
                        before, after)
    return response


def accept_task_with_successor(dossier, predecessor_oguid, response_text):
    predecessor = getUtility(ITaskQuery).get_task_by_oguid(predecessor_oguid)

    # XXX also transport responses

    # Transport the original task (predecessor) to this dossier. The new
    # response and task change is not yet done and will be done later. This
    # is necessary for beeing as transaction aware as possible.
    transporter = getUtility(ITransporter)
    successor = transporter.transport_from(
        dossier, predecessor.client_id, predecessor.physical_path)
    successor_tc = ISuccessorTaskController(successor)

    transport_task_documents(predecessor, successor)

    # First "accept" the successor task..
    accept_task_with_response(successor, response_text)

    transaction.savepoint()
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


def transport_task_documents(predecessor, target_task):
    """Transports documents related to or contained by the remote task with
    the `predecessor_oguid` to the local `target_task`.
    """

    transporter = getUtility(ITransporter)
    data = remote_json_request(predecessor.client_id,
                               '@@accept_task-extract_task_documents',
                               path=predecessor.physical_path)

    for item in data:
        item = encode_after_json(item)
        # XXX this creates responses, but maybe shouldnt
        transporter._create_object(target_task, item)


class ExtractTaskDocuments(grok.View):
    grok.context(ITask)
    grok.require('zope2.View')
    grok.name('accept_task-extract_task_documents')

    def render(self):
        transporter = getUtility(ITransporter)
        data = []

        for doc in self.get_documents():
            data.append(transporter._extract_data(doc))

        return json.dumps(data)

    def get_documents(self):
        """All documents which are either within the current task or defined
        as related items.
        """

        # find documents within the task
        brains = self.context.getFolderContents(
            full_objects=False,
            contentFilter={'portal_type': ['opengever.document.document',
                                           'ftw.mail.mail']})
        for doc in brains:
            yield doc.getObject()

        # find referenced documents
        relatedItems = getattr(self.context, 'relatedItems', None)
        if relatedItems:
            for rel in self.context.relatedItems:
                yield rel.to_object
