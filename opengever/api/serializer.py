from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.response import IResponseContainer
from opengever.base.response import IResponseSupported
from opengever.workspaceclient import is_workspace_client_feature_enabled
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.interface import implementer


def extend_with_bumblebee_checksum(result, context):
    if IBumblebeeable.providedBy(context):
        result['bumblebee_checksum'] = IBumblebeeDocument(context).get_checksum()


def extend_with_relative_path(result, context):
    url_tool = api.portal.get_tool(name='portal_url')
    result['relative_path'] = '/'.join(url_tool.getRelativeContentPath(context))


def extend_with_responses(result, context, request):
    if IResponseSupported.providedBy(context):
        result['responses'] = []
        for response in IResponseContainer(context).list():
            serializer = getMultiAdapter((response, request), ISerializeToJson)
            result['responses'].append(serializer(container=context))


def extend_with_workspaces(result, context):
    if not is_workspace_client_feature_enabled():
        return

    manager = queryAdapter(context, ILinkedWorkspaces)
    if manager:
        result['workspaces'] = manager.list()


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
        extend_with_workspaces(result, self.context)
        return result


@adapter(long)
@implementer(IJsonCompatible)
def long_converter(value):
    """Long is currently not supported by plone.restapi, but should be
    in a later release.
    """
    return value
