from ftw.upgrade import UpgradeStep
from plone import api
import uuid


class AddDefaultVideoconferencingURLsToWorkspaceObjects(UpgradeStep):
    """Add default videoconferencing URLs to workspace objects.
    """

    deferrable = True

    def __call__(self):
        base_url = api.portal.get_registry_record(
            'opengever.workspace.interfaces.IWorkspaceSettings.videoconferencing_base_url')
        base_url = base_url.rstrip('/')

        query = {
            'object_provides': 'opengever.workspace.interfaces.IWorkspace'
        }
        for workspace in self.objects(query, "Init videoconferencing URL."):
            # intitialize None so we have correct defaults
            if not base_url:
                workspace.videoconferencing_url = None
            else:
                workspace.videoconferencing_url = u'{}/{}'.format(
                    base_url, uuid.uuid4())
