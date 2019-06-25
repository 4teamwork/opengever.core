from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IWorkspace, Interface)
class SerializeWorkspaceToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceToJson, self).__call__(*args, **kwargs)

        manager = ManageParticipants(self.context, self.request)

        result[u"can_manage_participants"] = manager.can_manage_member()

        return result
