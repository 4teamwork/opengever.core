from DateTime import DateTime
from datetime import datetime
from five import grok
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.transport import ORIGINAL_INTID_ANNOTATION_KEY
from opengever.ogds.base.utils import encode_after_json
from opengever.ogds.base.utils import remote_json_request
from opengever.ogds.base.utils import remote_request
from opengever.task.adapters import IResponse as IPersistentResponse
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.response import Response
from opengever.task.task import ITask
from opengever.task.util import get_documents_of_task
from persistent.list import PersistentList
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.interface.interface import Attribute
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import modified
import json


class IResponseTransporter(Interface):
    pass


class ResponseTransporter(grok.Adapter):
    """Adadpter for sending responses of the adapted task to
    a remote task on a remote admin unit.
    """

    grok.context(ITask)
    grok.implements(IResponseTransporter)
    grok.require('zope2.View')

    def send_responses(self, target_cid, remote_task_url,
                       intids_mapping=None):
        """ Sends all responses of task self.context to task on
        a remote admin unit.
        `target_cid`: id of a target admin unit
        `remote_task_url`: url to a task on `target_cid` relative
        to its site root.
        `intids_mapping`: replace intids of RelationValues according
        to this mapping. This fixes the intids on remote admin unit.
        RelationValues not listed in this mapping will not be sent.
        """

        jsondata = self.extract_responses(intids_mapping)

        return remote_request(target_cid,
                                   '@@task-responses-receive',
                                   path=remote_task_url,
                                   data=dict(responses=jsondata))

    def get_responses(self, target_cid, remote_task_path, intids_mapping):
        """Retrieves all responses from the task with path `remote_task_path`
        on the admin_unit `target_cid` and adds them to the current context (target
        task).

        Provide a an `intids_mapping` (dict), mapping the original intids of
        related objects to the new intids of the copies on this admin_unit. This
        is necessary for fixing the relations.
        """

        req_data = {'intids_mapping': json.dumps(intids_mapping)}
        response = remote_request(target_cid,
                                  '@@task-responses-extract',
                                  path=remote_task_path,
                                  data=req_data)
        try:
            data = json.loads(response.read())
        except ValueError:
            #is a internal request
            data = response.read()

        self.create_responses(data)

    def extract_responses(self, intids_mapping=None):
        if intids_mapping is None:
            intids_mapping = {}

        self.intids_mapping = intids_mapping

        data = []
        for resp in IResponseContainer(self.context):
            resp_data = {}

            for key in IPersistentResponse.names():
                attr = IPersistentResponse[key]
                if type(attr) == Attribute:
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
            response = Response('')

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

        if type_ == 'datetime':
            return DateTime(val).asdatetime()

        if type_ == 'DateTime':
            return DateTime(val)

        if type_ == 'RelationValue':
            return RelationValue(val)

        if type_ == 'list':
            return [self._decode(item) for item in val]

        return val


class ReceiveResponses(grok.View):
    """Receives a json request cotnaining one or more responses to
    add to the context task.
    """

    grok.context(ITask)
    grok.name('task-responses-receive')
    grok.require('zope2.View')

    def render(self):
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
            return 'OK'

        transporter.create_responses(data)

        return 'ok'


class ExtractResponses(grok.View):
    grok.context(ITask)
    grok.name('task-responses-extract')
    grok.require('zope2.View')

    def render(self):
        intids_mapping = json.loads(self.request.get(
                'intids_mapping', '{}'))

        # json converts dict-keys to strings - but we need
        # keys and values as int
        intids_mapping = dict([(int(k), int(v))
                               for (k, v) in intids_mapping.items()])

        transporter = IResponseTransporter(self.context)
        return transporter.extract_responses(intids_mapping)


class TaskDocumentsTransporter(grok.GlobalUtility):
    grok.implements(ITaskDocumentsTransporter)

    def copy_documents_from_remote_task(self, task, target, documents=None):
        transporter = getUtility(ITransporter)
        data = remote_json_request(
            task.admin_unit_id,
            '@@task-documents-extract',
            path=task.physical_path,
            data={'documents': json.dumps(documents)})

        intids_mapping = {}
        intids = getUtility(IIntIds)

        for item in data:
            item = encode_after_json(item)
            obj = transporter._create_object(target, item)

            oldintid = IAnnotations(obj)[ORIGINAL_INTID_ANNOTATION_KEY]
            newintid = intids.getId(obj)
            intids_mapping[oldintid] = newintid

            # fire the added Event to automaticly create a inital version
            notify(ObjectAddedEvent(obj))

        return intids_mapping


class ExtractDocuments(grok.View):
    grok.context(ITask)
    grok.name('task-documents-extract')
    grok.require('zope2.View')

    def render(self):
        transporter = getUtility(ITransporter)
        data = []

        for doc in self.get_documents():
            data.append(transporter._extract_data(doc))

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
