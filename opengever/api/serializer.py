from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.response import IResponseContainer
from opengever.base.response import IResponseSupported
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter


def extend_with_bumblebee_checksum(result, context):
    if IBumblebeeable.providedBy(context):
        result['bumblebee_checksum'] = IBumblebeeDocument(context).get_checksum()


def extend_with_relative_path(result, context):
    url_tool = api.portal.get_tool(name='portal_url')
    result['relative_path'] = '/'.join(url_tool.getRelativeContentPath(context))


def extend_with_responses(result, context, request):
    if IResponseSupported.providedBy(context):
        result['responses'] = []
        for _id, response in IResponseContainer(context).items():
            serializer = getMultiAdapter((response, request), ISerializeToJson)
            result['responses'].append(
                serializer(container=context, response_id=_id))


@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverSerializeToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeToJson, self).__call__(*args, **kwargs)

        extend_with_bumblebee_checksum(result, self.context)
        extend_with_relative_path(result, self.context)
        extend_with_responses(result, self.context, self.request)

        return result


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class GeverSerializeFolderToJson(SerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeFolderToJson, self).__call__(*args, **kwargs)

        extend_with_relative_path(result, self.context)
        extend_with_responses(result, self.context, self.request)

        return result
