from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.participation import can_manage_member
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IWorkspace, Interface)
class SerializeWorkspaceToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceToJson, self).__call__(*args, **kwargs)

        result[u"can_manage_participants"] = can_manage_member(self.context)

        return result
