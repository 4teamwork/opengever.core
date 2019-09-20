from datetime import date
from DateTime import DateTime
from datetime import datetime
from opengever.base.request import dispatch_json_request
from opengever.base.request import dispatch_request
from opengever.base.request import tracebackify
from opengever.base.response import IResponseContainer
from opengever.base.transport import ORIGINAL_INTID_ANNOTATION_KEY
from opengever.base.transport import Transporter
from opengever.base.utils import ok_response
from opengever.document.versioner import Versioner
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.task import ITask
from opengever.task.task_response import ITaskResponse
from opengever.task.task_response import TaskResponse
from opengever.task.util import get_documents_of_task
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from Products.Five.browser import BrowserView
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.lifecycleevent import modified
import json


class IResponseTransporter(Interface):
    pass


@implementer(IResponseTransporter)
@adapter(ITask)
class ResponseTransporter(object):
    """Adadpter for sending responses of the adapted task to
    a remote task on a remote admin unit.
    """

    def __init__(self, context):
        self.context = context

    def send_responses(self, target_admin_unit_id, remote_task_url,
                       intids_mapping=None):
        """Sends all responses of task self.context to task on
        a remote admin unit.

        `target_admin_unit_id`: id of a target admin unit
        `remote_task_url`: url to a task on `target_cid` relative
        to its site root.
        `intids_mapping`: replace intids of RelationValues according
        to this mapping. This fixes the intids on remote admin unit.
        RelationValues not listed in this mapping will not be sent.

        """
        jsondata = self.extract_responses(intids_mapping)

        return dispatch_request(target_admin_unit_id,
                                '@@task-responses-receive',
                                path=remote_task_url,
                                data=dict(responses=jsondata))

    def get_responses(self, target_admin_unit_id, remote_task_path,
                      intids_mapping):
        """Retrieves all responses from the task with path `remote_task_path`
        on the admin_unit `target_admin_unit_id` and adds them to the current
        context (target task).

        Provide a an `intids_mapping` (dict), mapping the original intids of
        related objects to the new intids of the copies on this admin_unit.
        This is necessary for fixing the relations.

        """
        req_data = {'intids_mapping': json.dumps(intids_mapping)}
        response = dispatch_request(target_admin_unit_id,
                                    '@@task-responses-extract',
                                    path=remote_task_path,
                                    data=req_data)
        try:
            data = json.loads(response.read())
        except ValueError:
            # is a internal request
            data = response.read()

        self.create_responses(data)

    def extract_responses(self, intids_mapping=None):
        if intids_mapping is None:
            intids_mapping = {}

        self.intids_mapping = intids_mapping

        data = []
        for resp in IResponseContainer(self.context):
            resp_data = {}
            for key in list(ITaskResponse):
                val = getattr(resp, key, None)
                try:
                    val = self._encode(val)
                except ValueError:
                    # the intid in the relation value is not listed
                    # in the mapping - so we skip it.
                    pass
                else:
                    resp_data[key] = val
            data.append(resp_data)

        return json.dumps(data)

    def create_responses(self, data):
        container = IResponseContainer(self.context)

        for resp_data in data:
            response = TaskResponse('')

            for key, value in resp_data.items():
                if value:
                    value = self._decode(value)
                setattr(response, key, value)

            container.add(response)

        modified(self.context)

    def _encode(self, value):
        """Lazy encoding function.
        """

        if isinstance(value, str):
            return [u'string:utf8', value.decode('utf-8')]

        if isinstance(value, unicode):
            return [u'unicode', value]

        if isinstance(value, datetime):
            return [u'datetime', str(value)]

        if isinstance(value, date):
            return [u'date', str(value)]

        if isinstance(value, DateTime):
            return [u'DateTime', str(value)]

        if isinstance(value, (PersistentList, list)):
            return [u'list',
                    [self._encode(item) for item in value]]

        if isinstance(value, RelationValue):
            if value.to_id in self.intids_mapping:
                return [u'RelationValue',
                        self.intids_mapping[value.to_id]]
            else:
                raise ValueError('intids of relation value not in '
                                 'mapping')

        if isinstance(value, (PersistentDict, dict)):
            return [u'dict',
                    dict((k, self._encode(v)) for (k, v) in value.items())]

        return value

    def _decode(self, value):
        """Decode the previously encoded value.
        """

        if not isinstance(value, list):
            return value

        if not value or not isinstance(value[0], unicode):
            return value

        type_, val = value

        if type_.startswith('string:'):
            return val.encode(type_.split(':', 1)[1])

        if type_ == 'unicode':
            return unicode(val)

        if type_ == 'DateTime':
            return DateTime(val)

        if type_ == 'datetime':
            return DateTime(val).asdatetime()

        if type_ == 'date':
            return DateTime(val).asdatetime().date()

        if type_ == 'RelationValue':
            return RelationValue(val)

        if type_ == 'list':
            return [self._decode(item) for item in val]

        if type_ == 'dict':
            return dict((k, self._decode(v)) for (k, v) in val.items())

        return val


@tracebackify
class ReceiveResponses(BrowserView):
    """Receives a json request cotnaining one or more responses to
    add to the context task.
    """

    def __call__(self):
        rawdata = self.request.get('responses')
        data = json.loads(rawdata)

        transporter = IResponseTransporter(self.context)
        current_data = json.loads(transporter.extract_responses())
        if current_data == data:
            # In case of a conflict error while committing on the
            # source admin_unit this view is called twice or more. If the
            # current_data and data maches, it is not the first
            # request and we are in conflict resolution. Thus for not
            # duplicating responses we abort with "OK" (since we have
            # already this exact task in a earlier request).
            return ok_response(self.request)

        transporter.create_responses(data)

        return ok_response(self.request)


@tracebackify
class ExtractResponses(BrowserView):

    def __call__(self):
        intids_mapping = json.loads(self.request.get(
            'intids_mapping', '{}'))

        # json converts dict-keys to strings - but we need
        # keys and values as int
        intids_mapping = dict([(int(k), int(v))
                               for (k, v) in intids_mapping.items()])

        transporter = IResponseTransporter(self.context)
        return transporter.extract_responses(intids_mapping)


@implementer(ITaskDocumentsTransporter)
class TaskDocumentsTransporter(object):

    def copy_documents_from_remote_task(self, task, target,
                                        documents=None, comment=None):

        transporter = Transporter()
        data = dispatch_json_request(
            task.admin_unit_id,
            '@@task-documents-extract',
            path=task.physical_path,
            data={'documents': json.dumps(documents)})

        intids_mapping = {}
        intids = getUtility(IIntIds)

        for item in data:
            obj = transporter.create(item, target)

            # Set custom initial version comment
            if comment:
                Versioner(obj).set_custom_initial_version_comment(comment)

            oldintid = IAnnotations(obj)[ORIGINAL_INTID_ANNOTATION_KEY]
            newintid = intids.getId(obj)
            intids_mapping[oldintid] = newintid

        return intids_mapping


class ExtractDocuments(BrowserView):

    def __call__(self):
        transporter = Transporter()
        data = []

        for doc in self.get_documents():
            data.append(transporter.extract(doc))

        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps(data)

    def get_documents(self):

        documents = json.loads(self.request.get('documents'))
        documents = documents and [int(iid) for iid in documents]
        intids = getUtility(IIntIds)

        for doc in get_documents_of_task(self.context, include_mails=True):
            if documents is None or intids.getId(doc) in documents:
                yield doc
