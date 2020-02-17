from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import NotFound
from zope.interface import alsoProvides


class LinkedWorkspacesPost(Service):
    """API Endpoint to add a new linked workspace.
    """

    def reply(self):
        if not is_workspace_client_feature_available():
            raise NotFound

        if self.context.is_subdossier():
            raise NotFound

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Validation will be done on the remote system
        data = json_body(self.request)

        return ILinkedWorkspaces(self.context).create(**data)
