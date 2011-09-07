from DateTime import DateTime
from datetime import datetime
from five import grok
from opengever.ogds.base.utils import remote_request
from opengever.task.adapters import IResponse as IPersistentResponse
from opengever.task.adapters import IResponseContainer
from opengever.task.response import Response
from opengever.task.task import ITask
from persistent.list import PersistentList
from z3c.relationfield import RelationValue
from zope.interface import Interface
from zope.interface.interface import Attribute
from zope.lifecycleevent import modified
import json


class IResponseTransporter(Interface):
    pass


class ResponseTransporter(grok.Adapter):
    """Adadpter for sending responses of the adapted task to
    a remote task on a remote client.
    """

    grok.context(ITask)
    grok.implements(IResponseTransporter)
    grok.require('zope2.View')

    def send_responses(self, target_cid, remote_task_url,
                       intids_mapping={}):
        """ Sends all responses of task self.context to task on
        a remote client.
        `target_cid`: client_id of a target client
        `remote_task_url`: url to a task on `target_cid` relative
        to its site root.
        `intids_mapping`: replace intids of RelationValues according
        to this mapping. This fixes the intids on remote clients.
        RelationValues not listed in this mapping will not be sent.
        """
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

        jsondata = json.dumps(data)

        return remote_request(target_cid,
                                   '@@task-responses-receive',
                                   path=remote_task_url,
                                   data=dict(responses=jsondata))

    def _encode(self, value):
        """Lazy encoding function.
        """

        if isinstance(value, str):
            return ('string:utf8', value.decode('utf-8'))

        if isinstance(value, unicode):
            return ('unicode', value)

        if isinstance(value, datetime):
            return ('datetime', str(value))

        if isinstance(value, DateTime):
            return ('DateTime', str(value))

        if isinstance(value, PersistentList):
            return list(value)

        if isinstance(value, RelationValue):
            if value.to_id in self.intids_mapping:
                return ('RelationValue',
                        self.intids_mapping[value.to_id])
            else:
                raise ValueError('intids of relation value not in '
                                 'mapping')

        return value




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

        container = IResponseContainer(self.context)

        for resp_data in data:
            response = Response('')

            for key, value in resp_data.items():
                if value:
                    value = self._decode(value)
                setattr(response, key, value)

            container.add(response)

        modified(self.context)
        return 'ok'

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

        return val
