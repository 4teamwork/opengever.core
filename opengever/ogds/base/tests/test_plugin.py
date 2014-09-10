from opengever.ogds.base.Extensions.plugins import authenticate_credentials
from opengever.ogds.base.Extensions.plugins import extract_user
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.testing import FunctionalTestCase
from ftw.builder import create
from ftw.builder import Builder


class TestRemoteAuthenticationPlugin(FunctionalTestCase):

    use_default_fixture = False

    def set_params_for_remote_request(self, userid='hugo.boss',
                                      clientid='client1', client_ip=None):

        self.portal.REQUEST.environ['X_OGDS_AC'] = userid
        self.portal.REQUEST.environ['X_OGDS_AUID'] = clientid
        self.portal.REQUEST.environ['REMOTE_HOST'] = 'http://nohost/client1'
        self.portal.REQUEST._client_addr = client_ip

    def test_successfull_credentials_authentication_returns_a_tuple_with_the_userid(self):
        ip = '192.168.1.233'
        create(Builder('admin_unit')
               .id('client1')
               .having(title=u'Client1', ip_address=ip))

        self.set_params_for_remote_request(client_ip=ip)

        creds = extract_user(self.portal, self.portal.REQUEST)
        self.assertEquals(
            {'login': 'hugo.boss',
             'remote_host': 'http://nohost/client1',
             'id': 'hugo.boss',
             'remote_address': '192.168.1.233', 'auid': 'client1'},
            creds)

        self.assertEquals(
            ('hugo.boss', 'hugo.boss'),
            authenticate_credentials(self.portal, creds))

    def test_after_successfully_credentials_authentication_the_request_provides_the_internal_request_layer(self):
        ip = '192.168.1.233'
        create(Builder('admin_unit')
               .id('client1')
               .having(title=u'Client1', ip_address=ip))

        self.set_params_for_remote_request(client_ip=ip)

        creds = extract_user(self.portal, self.portal.REQUEST)
        authenticate_credentials(self.portal, creds)

        self.assertTrue(
            IInternalOpengeverRequestLayer.providedBy(self.portal.REQUEST))

    def test_credentials_authentication_works_also_with_a_coma_sepereted_list(self):
        """The plugin should also work with a client with a comma
        seperated list of ip_adresses. """

        create(Builder('admin_unit')
               .id('client1')
               .having(title=u'Client1',
                       ip_address='192.168.1.53,192.168.1.2'))

        self.set_params_for_remote_request(client_ip='192.168.1.2')

        creds = extract_user(self.portal, self.portal.REQUEST)
        self.assertEquals(
            ('hugo.boss', 'hugo.boss'),
            authenticate_credentials(self.portal, creds))

    def test_credentials_authentication_for_invalid_ip_returns_none(self):
        create(Builder('admin_unit')
               .id('client1')
               .having(title=u'Client1', ip_address='192.186.1.1'))

        self.set_params_for_remote_request(client_ip='192.168.1.233')

        creds = extract_user(self.portal, self.portal.REQUEST)
        self.assertEquals(None, authenticate_credentials(self.portal, creds))

    def test_credentials_authentication_from_a_not_existig_client_returns_none(self):
        ip_address='192.186.1.1'

        create(Builder('admin_unit')
               .id('client1')
               .having(title=u'Client1', ip_address=ip_address))

        self.set_params_for_remote_request(clientid='client3', client_ip='192.168.1.1')

        creds = extract_user(self.portal, self.portal.REQUEST)
        self.assertEquals(None, authenticate_credentials(self.portal, creds))
