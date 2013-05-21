from opengever.ogds.base.Extensions.plugins import authenticate_credentials
from opengever.ogds.base.Extensions.plugins import extract_user
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.utils import create_session
from opengever.testing import FunctionalTestCase


class TestRemoteAuthenticationPlugin(FunctionalTestCase):

    def setUp(self):
        super(TestRemoteAuthenticationPlugin, self).setUp()

        self.request = self.layer['request']

    def test_plugins(self):
        # ip definitions:
        client1_ip = '192.168.1.233'

        # create_clients:
        session = create_session()
        _create_example_client(session, 'client1',
                                   {'title': 'Client 1',
                                    'ip_address': client1_ip,
                                    'site_url': 'http://nohost/client1',
                                    'public_url': 'http://nohost/client1',
                                    'group': 'client1_users',
                                    'inbox_group': 'client1_inbox_users'})

        # the ip_address column should also work with a comma seperated list

        _create_example_client(session, 'client3',
                                   {'title': 'Client 3',
                                    'ip_address': '192.168.1.53,192.168.1.2',
                                    'site_url': 'http://nohost/client3',
                                    'public_url': 'http://nohost/client3',
                                    'group': 'client3_users',
                                    'inbox_group': 'client3_inbox_users'})


        # extract_user:

        # fake the request
        self.request.environ['X_OGDS_AC']='hugo.boss'
        self.request.environ['X_OGDS_CID']='client1'
        self.request.environ['REMOTE_HOST']='http://nohost/client1'
        self.request._client_addr=client1_ip

        class Context(object): pass
        obj = Context()
        obj.REQUEST = self.request

        creds = extract_user(obj, self.request)
        self.assertEquals(
            {'login': 'hugo.boss',
             'remote_host': 'http://nohost/client1',
             'id': 'hugo.boss',
             'remote_address': '192.168.1.233', 'cid': 'client1'},
            creds)

        self.assertEquals(
            ('hugo.boss', 'hugo.boss'), authenticate_credentials(obj, creds))

        # fake a bad request (client != ip)
        self.request.environ['X_OGDS_CID']='client3'
        creds = extract_user(obj, self.request)
        self.assertEquals(None, authenticate_credentials(obj, creds))

        # the plugin should also work with a client with a comma seperated list of ip_adresses
        self.request._client_addr='192.168.1.2'
        creds = extract_user(obj, self.request)
        self.assertEquals(
            ('hugo.boss', 'hugo.boss'), authenticate_credentials(obj, creds))
