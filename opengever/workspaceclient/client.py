from opengever.workspace import DEACTIVATE_WORKSPACE_TRANSITION
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.session import WorkspaceSession
from plone import api
from zExceptions import Unauthorized
import json
import os


class WorkspaceClient(object):
    """The client is used for communicating with a workspace through the
    REST API. It is instantiated for the current logged in user.
    """

    @property
    def session(self):
        """We always need to invoke a new workspace-session. Otherwise it is
        possible to dispatch a request with another users session.
        """
        if not is_workspace_client_feature_available():
            raise WorkspaceClientFeatureNotEnabled()

        if not self.workspace_url:
            raise WorkspaceURLMissing()

        if not api.user.has_permission('opengever.workspaceclient: Use Workspace Client'):
            raise Unauthorized("User does not have permission to use the WorkspaceClient")
        return WorkspaceSession(self.workspace_url,
                                api.user.get_current().getUserName())

    @property
    def request(self):
        """Returns the request object from the current session.
        """
        return self.session.request

    @property
    def workspace_url(self):
        """Retruns the configured workspace url in the env variable.
        """
        return os.environ.get('TEAMRAUM_URL', '').strip('/')

    def search(self, url_or_path='', **kwargs):
        """Dispatches a search request to the given url or path.
        """
        url_or_path = '{}/@search'.format(url_or_path.strip('/'))
        return self.request.get(url_or_path, params=kwargs).json()

    def solrsearch(self, **kwargs):
        """Dispatches a solrsearch request.
        """
        return self.request.get('/@solrsearch', params=kwargs).json()

    def get(self, url_or_path):
        """Proxy method to perform a get request.
        """
        return self.request.get(url_or_path).json()

    def post(self, url_or_path, *args, **kwargs):
        """Proxy method to perform a post request.
        """
        return self.request.post(url_or_path, *args, **kwargs).json()

    def patch(self, url_or_path, *args, **kwargs):
        """Proxy method to perform a patch request.
        """
        return self.request.patch(url_or_path, *args, **kwargs).json()

    def create_workspace(self, **data):
        """Crates a new workspace and returns the serialization of the new
        workspace
        """
        payload = data
        payload.update({
            '@type': 'opengever.workspace.workspace'
        })

        return self.request.post('/workspaces', json=payload).json()

    def get_gever_url(self, oguid):
        return '{}/@resolve-oguid?oguid={}'.format(api.portal.get().absolute_url(), oguid)

    def link_to_workspace(self, workspace_uid, dossier_oguid):
        """ Sets dossier_oguid as external_reference of the workspace
        and returns the serialization of the workspace
        """
        workspace = self.get_by_uid(uid=workspace_uid, metadata_fields='external_reference')
        if workspace.get('external_reference'):
            raise LookupError("Workspace is already linked to a dossier")
        return self.request.patch(workspace.get('@id'),
                                  json={'external_reference': dossier_oguid,
                                        'gever_url': self.get_gever_url(dossier_oguid)},
                                  headers={'Prefer': 'return=representation'}).json()

    def update_dossier_uid(self, workspace_uid, new_dossier_oguid):
        """Updates external_reference on the remote workspace."""

        workspace = self.get_by_uid(uid=workspace_uid)
        return self.request.patch(
            workspace.get('@id'),
            json={'external_reference': new_dossier_oguid,
                  'gever_url': self.get_gever_url(new_dossier_oguid)})

    def deactivate_workspace(self, workspace_url):
        """Deactivates workspace"""
        return self.request.post('{}/@workflow/{}'.format(workspace_url,
                                                          DEACTIVATE_WORKSPACE_TRANSITION))

    def is_workspace_deactivation_transition_available(self, workspace_url):
        workflow_url = '{}/@workflow'.format(workspace_url)
        response = self.request.get(workflow_url).json()
        transition_url = '{}/{}'.format(workflow_url, DEACTIVATE_WORKSPACE_TRANSITION)
        transition_ids = [transition['@id'] for transition in response.get('transitions', [])]
        return transition_url in transition_ids

    def unlink_workspace(self, workspace_uid):
        """Removes external_reference on the workspace"""

        workspace = self.get_by_uid(uid=workspace_uid)
        workspace_url = workspace.get('@id').strip('/')
        self.request.post(workspace_url + '/@remove-dossier-reference')
        return workspace

    def get_by_uid(self, uid, **kwargs):
        """Searches on the remote system for an object having the given UID
        and returns it (serialized).
        """
        items = self.search(UID=uid, **kwargs).get('items')

        if not items:
            raise LookupError("Did not find object with UID {}".format(uid))

        if len(items) > 1:
            raise LookupError("Found multiple objects with the same UID")

        return items[0]

    def lookup_url_by_uid(self, uid):
        """Searches on the remote system for an object having the given UID and
        returns the URL to this object.
        """
        return self.get_by_uid(uid).get('@id')

    def upload_document_copy(self, url_or_path, file_, content_type,
                             filename, document_metadata, gever_document_uid):
        """Creates a copy of a GEVER document in a workspace or folder.

        :param url_or_path: Location where to create the new document
        :param file_: Readable IO which holds the content of the file
        :param content_type: The content type of the document
        :param filename: The filename of the document
        :param document_metadata: Additional metadatadata for the new object
        :param gever_document_uid: UID of the GEVER document being copied
        """
        url_or_path = url_or_path.strip('/')

        response = self.post(
            url_or_path + '/@upload-document-copy',
            files={'file': (filename, file_, content_type)},
            data={
                'document_metadata': json.dumps(document_metadata),
                'gever_document_uid': gever_document_uid,
            }
        )
        return response

    def trash_document(self, document_url):
        """Trashes the specified teamraum document.
        """
        response = self.request.post(document_url + '/@trash')
        response.raise_for_status()
        return response
