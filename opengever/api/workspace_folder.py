from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.trash.trash import ITrasher
from opengever.workspace.interfaces import IWorkspaceFolder
from zope.component import adapter
from zope.interface import Interface


@adapter(IWorkspaceFolder, Interface)
class SerializeWorkspaceFolderToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceFolderToJson, self).__call__(*args, **kwargs)
        result["trashed"] = ITrasher(self.context).is_trashed()
        return result
