from ftw.mail.interfaces import IEmailAddress
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.trash.trash import ITrasher
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.utils import get_containing_workspace
from zope.component import adapter
from zope.interface import Interface


@adapter(IWorkspaceFolder, Interface)
class SerializeWorkspaceFolderToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceFolderToJson, self).__call__(*args, **kwargs)
        result[u'email'] = IEmailAddress(self.request).get_email_for_object(self.context)
        result["trashed"] = ITrasher(self.context).is_trashed()
        result[u"can_access_members"] = get_containing_workspace(
            self.context).access_members_allowed()
        return result
