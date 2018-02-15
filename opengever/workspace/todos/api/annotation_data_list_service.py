from opengever.workspace.interfaces import IAnnotationDataList
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.interface import implements
from zope.interface import Invalid
from zope.publisher.interfaces import IPublishTraverse


class AnnotationDataListService(Service):

    name = None  # @<name> of the service
    data_list_adapter_interface = None

    def __init__(self, context, request):
        super(AnnotationDataListService, self).__init__(context, request)
        if self.name is None:
            raise ValueError('Require self.name')
        if self.data_list_adapter_interface is None:
            raise ValueError('Require self.data_list_adapter_interface')
        if not issubclass(self.data_list_adapter_interface,
                          IAnnotationDataList):
            raise ValueError('{!r} must be a subclass of {!r}'.format(
                self.data_list_adapter_interface, IAnnotationDataList))

    @property
    def data_list_adapter(self):
        if getattr(self, '_data_list_adapter', None) is None:
            self._data_list_adapter = self.data_list_adapter_interface(
                self.context)
        return self._data_list_adapter

    def prepare_item_for_json(self, item):
        data = item.as_json_compatible()
        data['@id'] = '{}/@{}/{}'.format(self.context.absolute_url(),
                                         self.name,
                                         item.id)
        return data

    def get_payload(self):
        request_data = json_body(self.request)
        writeable_attributes = self.data_list_adapter.writeable_attributes
        for key in request_data:
            if key not in writeable_attributes:
                raise Forbidden(
                    'Disallowed attribute {!r}. Allowed: {!r}'.format(
                        key, writeable_attributes))

        return request_data


class TraversableAnnotationDataListService(AnnotationDataListService):
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(TraversableAnnotationDataListService, self).__init__(
            context, request)
        self.item_id = None

    def publishTraverse(self, request, item_id):
        if self.item_id or not item_id:
            raise BadRequest('Invalid URL')
        self.item_id = int(item_id)
        return self

    def get_requested_item(self):
        if not self.item_id:
            raise BadRequest(
                'Require item id in URL: /@' + self.name + '/[ID]')

        try:
            return self.data_list_adapter.get(self.item_id)
        except KeyError:
            raise BadRequest('Item {!r} not found.'.format(self.item))


class GETService(TraversableAnnotationDataListService):

    def reply(self):
        if self.item_id:
            return self.prepare_item_for_json(self.get_requested_item())

        return {'@id': '{}/@{}'.format(self.context.absolute_url(), self.name),
                'items': map(self.prepare_item_for_json,
                             self.data_list_adapter.all())}


class POSTService(AnnotationDataListService):

    def reply(self):
        try:
            return self.prepare_item_for_json(
                self.data_list_adapter.create(**self.get_payload()))
        except Invalid, exc:
            raise BadRequest('{}: {}'.format(exc.__class__.__name__, exc))


class PATCHService(TraversableAnnotationDataListService):

    def reply(self):
        try:
            return self.prepare_item_for_json(
                self.get_requested_item().update(**self.get_payload()))
        except Invalid, exc:
            raise BadRequest('{}: {}'.format(exc.__class__.__name__, exc))


class DELETEService(TraversableAnnotationDataListService):

    def reply(self):
        self.data_list_adapter.remove(self.get_requested_item())
        self.request.response.setStatus(204)


def build_services(service_name, adapter_interface):

    class Get(GETService):
        name = service_name
        data_list_adapter_interface = adapter_interface

    class Post(POSTService):
        name = service_name
        data_list_adapter_interface = adapter_interface

    class Patch(PATCHService):
        name = service_name
        data_list_adapter_interface = adapter_interface

    class Delete(DELETEService):
        name = service_name
        data_list_adapter_interface = adapter_interface

    return {
        'Get': Get,
        'Post': Post,
        'Patch': Patch,
        'Delete': Delete,
    }
