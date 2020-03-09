from base64 import b64encode
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.session import WorkspaceSession
from plone import api
from Products.CMFDiffTool.utils import safe_utf8
from zExceptions import Unauthorized
import os


class WorkspaceClient(object):
    """The client is used for communicating with a workspace through the
    REST API. It is instantiated for the current logged in user.
    """

    def __init__(self):
        if not is_workspace_client_feature_available():
            raise WorkspaceClientFeatureNotEnabled()

        if not self.workspace_url:
            raise WorkspaceURLMissing()

    @property
    def session(self):
        """We always need to invoke a new workspace-session. Otherwise it is
        possible to dispatch a request with another users session.
        """
        if not api.user.has_permission('opengever.workspaceclient: Use Workspace Client'):
            raise Unauthorized("User does not have permission to use the WorkspaceClient")
        return WorkspaceSession(self.workspace_url,
                                api.user.get_current().getId())

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

    def lookup_url_by_uid(self, uid):
        """Searches on the remote system for an object having the given UID and
        returns the URL to this object.

        If no object is found with the given UID, it returns None.
        """
        items = self.search(UID=uid).get('items')

        if not items:
            raise LookupError("Did not find object with UID {}".format(uid))

        if len(items) > 1:
            raise LookupError("Found multiple objects with the same UID")

        return items[0].get('@id') if items else None

    def tus_upload(self, url_or_path, portal_type, file_, size, content_type,
                   filename, **additional_metadata):
        """Creates a new file within the folder of the given url or path and
        extends the created file with some additional metadata.

        :param url_or_path: Location where to create the new document
        :param file: Readable IO which holds the content of the file
        :param size: The size of the file
        :param content_type: The content type of the document
        :param filename: The filename of the document
        :param additional_metadata: Additional metadatadata for the new object
        """
        url_or_path = url_or_path.strip('/')
        metadata = {
            'filename': filename,
            '@type': portal_type,
            'content_type': content_type
        }

        tus = self.request.post('{}/@tus-upload'.format(url_or_path), headers={
            'Tus-Resumable': '1.0.0',
            'Upload-Length': str(size),
            'Upload-Metadata': self._tus_metadata_string(metadata),
        })

        created_obj = self.request.patch(
            tus.headers['Location'],
            headers={
                'Tus-Resumable': '1.0.0',
                'Upload-Offset': '0',
                'Content-Type': 'application/offset+octet-stream'
            },
            data=file_,
        )

        obj_url = created_obj.headers['Location']

        # It's not possible to directly update the metadata of an object through
        # a TUS-request. We perform another patch-request to update the newly
        # created document with some additional metadata.
        if portal_type == "ftw.mail.mail":
            # patching E-mails would require manager permissions
            # on the remote system.
            return self.get(obj_url)

        return self.patch(obj_url, json=additional_metadata,
                          headers={'Prefer': 'return=representation'})

    def _tus_metadata_string(self, metadata):
        """We can pass metadata in the request header of a TUS-request.

        The 'Upload-Metadata' header contains a string of key-value pairs where
        the values are base64 encoded.

        This function converts a dict into a tus metadata string.
        """
        metadata_items = []
        for key, value in metadata.items():
            b64_value = str(b64encode(safe_utf8(value)))
            metadata_items.append('{} {}'.format(key, b64_value))

        return ','.join(metadata_items)
