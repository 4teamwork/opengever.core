from opengever.ogds.base.Extensions.plugins import authenticate_credentials
from opengever.ogds.base.Extensions.plugins import extract_user
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client


class TestRemoteAuthenticationPlugin(FunctionalTestCase):

    def setUp(self):
        super(TestRemoteAuthenticationPlugin, self).setUp()
        self.request = self.layer['request']

    def test_plugin_with_valid_request(self):
        client_ip = '192.168.1.233'
        create_client('client1', ip_address=client_ip)

        # fake a remote request
        self.request.environ['X_OGDS_AC'] = 'hugo.boss'
        self.request.environ['X_OGDS_CID'] = 'client1'
        self.request.environ['REMOTE_HOST'] = 'http://nohost/client1'
        self.request._client_addr = client_ip

        self.portal.REQUEST = self.request

        creds = extract_user(self.portal, self.request)
        self.assertEquals(
            {'login': 'hugo.boss',
             'remote_host': 'http://nohost/client1',
             'id': 'hugo.boss',
             'remote_address': '192.168.1.233', 'cid': 'client1'},
            creds)

        self.assertEquals(
            ('hugo.boss', 'hugo.boss'),
            authenticate_credentials(self.portal, creds))

        self.assertTrue(
            IInternalOpengeverRequestLayer.providedBy(self.request))

    def test_plugin_with_multiple_valid_ips(self):
        """The plugin should also work with a client with a comma
        seperated list of ip_adresses. """

        create_client('client1', ip_address='192.168.1.53,192.168.1.2')

        # fake a remote request
        self.request.environ['X_OGDS_AC'] = 'hugo.boss'
        self.request.environ['X_OGDS_CID'] = 'client1'
        self.request.environ['REMOTE_HOST'] = 'http://nohost/client1'
        self.request._client_addr = '192.168.1.2'
        self.portal.REQUEST = self.request

        creds = extract_user(self.portal, self.request)
        self.assertEquals(
            ('hugo.boss', 'hugo.boss'),
            authenticate_credentials(self.portal, creds))

    def test_plugin_from_invalid_ip(self):
        create_client('client1', ip_address='192.186.1.1')

        # fake a remote request
        self.request.environ['X_OGDS_AC'] = 'hugo.boss'
        self.request.environ['X_OGDS_CID'] = 'client1'
        self.request.environ['REMOTE_HOST'] = 'http://nohost/client1'
        self.request._client_addr = '192.168.1.233'
        self.portal.REQUEST = self.request

        creds = extract_user(self.portal, self.request)
        self.assertEquals(None, authenticate_credentials(self.portal, creds))

    def test_plugin_from_not_existing_client(self):
        create_client('client1', ip_address='192.186.1.1')

        # fake a remote request
        self.request.environ['X_OGDS_AC'] = 'hugo.boss'
        self.request.environ['X_OGDS_CID'] = 'client3'
        self.request.environ['REMOTE_HOST'] = 'http://nohost/client1'
        self.request._client_addr = '192.168.1.1'
        self.portal.REQUEST = self.request

        creds = extract_user(self.portal, self.request)
        self.assertEquals(None, authenticate_credentials(self.portal, creds))
