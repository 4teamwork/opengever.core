from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.workspace.interfaces import IWorkspaceMeeting
from opengever.workspace.interfaces import IWorkspaceMeetingAttendeesPresenceStateStorage
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IWorkspaceMeeting, Interface)
class SerializeWorkspaceMeetingToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceMeetingToJson, self).__call__(*args, **kwargs)
        storage = IWorkspaceMeetingAttendeesPresenceStateStorage(self.context)
        result['attendees_presence_states'] = storage.get_all()
        return result
