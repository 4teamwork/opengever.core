from opengever.workspace.base import WorkspaceBase
from opengever.workspace.interfaces import IWorkspace
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch
from plone.supermodel import model
from zExceptions import Unauthorized
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IWorkspaceSchema(model.Schema):
    """ """


class Workspace(WorkspaceBase):
    implements(IWorkspace)

    def get_parent_with_local_roles(self):
        return self


class WorkspaceContentPatch(ContentPatch):
    """Workspace specific PATCH service, which allows updating the content
    order without ModifyPortalContent permission. It checks instead for the
    specific `Update Content Order` permission
    """

    def reply(self):
        data = json_body(self.request)
        if data.keys() != ['ordering']:
            if not api.user.has_permission('Modify portal content',
                                           obj=self.context):
                raise Unauthorized()

        return super(WorkspaceContentPatch, self).reply()
