from opengever.workspace.interfaces import IWorkspace
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


# Convert sets the creator as the responsible.
# See https://github.com/4teamwork/opengever.core/issues/5557
@implementer(IDeserializeFromJson)
@adapter(IWorkspace, Interface)
class DeserializeWorkspaceFromJson(DeserializeFromJson):

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        # Never update the responsible
        if 'responsible' in data:
            del data['responsible']

        if create:
            # Set the current user as responsible on creating the object.
            data['responsible'] = api.user.get_current().getId()

        return super(DeserializeWorkspaceFromJson, self).__call__(
            validate_all, data, create)
