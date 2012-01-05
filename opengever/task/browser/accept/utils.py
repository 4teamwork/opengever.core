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
from persistent.dict import PersistentDict
from zope.component import getUtility
from zope.interface import Interface
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
    request_data = {'text': response_text,
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


# XXX: session is zeo-client specific, we need to find another solution
class AcceptTaskSessionDataManager(object):

    KEY = 'accept-task-wizard'

    def __init__(self, request):
        self.request = request
        self.oguid = self.request.get('oguid')
        assert self.oguid, 'Could not find "oguid" in request.'
        self.session = request.SESSION

    def get_data(self):
        if self.KEY not in self.session.keys():
            self.session[self.KEY] = PersistentDict()

        wizard_data = self.session[self.KEY]

        if self.oguid not in wizard_data:
            wizard_data[self.oguid] = PersistentDict()

        return wizard_data[self.oguid]

    def get(self, key, default=None):
        return self.get_data().get(key, default)

    def set(self, key, value):
        self.get_data()[key] = value

    def update(self, data):
        self.get_data().update(data)

    def push_to_foreign_client(self, client_id):
        data = {'session-data': json.dumps(dict(self.get_data())),
                'oguid': self.oguid}
        response = remote_request(client_id,
                                  '@@accept_task_receive_session_data',
                                  data=data)

        if response.read().strip() != 'OK':
            raise Exception('Could not push session data to client %s' % (
                    client_id))


class ReceiveSessionData(grok.View):
    """This view is used to update the session data. The session data manager
    calls this view on a remote client for pushing the data to the target
    client.
    """

    grok.context(Interface)
    grok.name('accept_task_receive_session_data')
    grok.require('zope2.View')

    def render(self):
        jsondata = self.request.get('session-data')
        data = json.loads(jsondata)

        AcceptTaskSessionDataManager(self.request).update(data)
        return 'OK'
