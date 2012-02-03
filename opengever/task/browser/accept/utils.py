from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import change_task_workflow_state
from zope.component import getUtility
import transaction


def accept_task_with_response(task, response_text, successor_oguid=None):
    transition = 'task-transition-open-in-progress'
    response = change_task_workflow_state(task,
                                          transition,
                                          text=response_text,
                                          successor_oguid=successor_oguid)

    return response


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
    intids_mapping = doc_transporter.copy_documents_from_remote_task(
        predecessor, successor)

    # copy the responses
    response_transporter = IResponseTransporter(successor)
    response_transporter.get_responses(predecessor.client_id,
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
        text = self.request.get('text')
        successor_oguid = self.request.get('successor_oguid')

        accept_task_with_response(self.context, text,
                                  successor_oguid=successor_oguid)
        return 'OK'
