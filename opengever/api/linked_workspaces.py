from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import alsoProvides


class LinkedWorkspacesService(Service):
    def reply(self):
        if not is_workspace_client_feature_available():
            raise NotFound

        return super(LinkedWorkspacesService, self).reply()


class LinkedWorkspacesGet(LinkedWorkspacesService):
    """API Endpoint to get all linked workspaces for a specific context
    """
    def reply(self):
        super(LinkedWorkspacesGet, self).reply()

        if self.context.is_subdossier():
            raise BadRequest

        response = ILinkedWorkspaces(self.context).list()

        # The response id contains the url of the workspace-client request.
        # We don't want to send it back to the client. We replace it with the
        # actual client request url.
        response['@id'] = self.request.getURL()

        return response


class LinkedWorkspacesPost(LinkedWorkspacesService):
    """API Endpoint to add a new linked workspace.
    """

    def reply(self):
        super(LinkedWorkspacesPost, self).reply()

        if self.context.is_subdossier():
            raise BadRequest

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Validation will be done on the remote system
        data = json_body(self.request)

        return ILinkedWorkspaces(self.context).create(**data)
