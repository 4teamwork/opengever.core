from DateTime import DateTime
from ftw.builder import builder_registry
from ftw.tokenauth.pas.storage import CredentialStorage
from ftw.tokenauth.service_keys.key_generation import create_service_key_pair
from opengever.workspaceclient.keys import key_registry
from zope.component.hooks import getSite


class WorkspaceTokenAuthAppBuilder(object):
    """Creates a workspace service key and registers it properly.
    """

    def __init__(self, session):
        self.session = session
        self.portal = getSite()
        self.arguments = {
            'client_id': 'default-client-id',
            'title': 'Test Key',
        }
        self.uri(self.portal.absolute_url())

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def issuer(self, user):
        self.having(user_id=user.getId())
        return self

    def uri(self, uri):
        uri = '{}/@@oauth2-token'.format(uri.strip('/'))
        self.having(token_uri=uri)
        return self

    def create(self, **kwargs):
        # Create a new keypair
        private_key, service_key = create_service_key_pair(
            self.arguments.get('user_id'),
            self.arguments.get('title'),
            self.arguments.get('token_uri'),
            self.arguments.get('ip_range'),
        )
        # Register the service app (server side)
        plugin = getSite().acl_users.token_auth
        credential_storage = CredentialStorage(plugin)
        credential_storage.add_service_key(service_key)

        # Regsister the service app (client side)
        service_key_client = {'private_key': private_key}
        service_key_client.update(service_key)
        service_key_client['issued'] = DateTime(service_key_client['issued']).asdatetime()
        del service_key_client['public_key']

        key_registry.add_key(service_key_client)

        return service_key_client


builder_registry.register('workspace_token_auth_app', WorkspaceTokenAuthAppBuilder)
