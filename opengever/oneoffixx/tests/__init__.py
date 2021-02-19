from opengever.oneoffixx.api_client import OneoffixxAPIClient
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.testing import IntegrationTestCase
from plone import api
import json
import requests
import requests_mock


class BaseOneOffixxTestCase(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    template_word = {
        'id': '2574d08d-95ea-4639-beab-3103fe4c3bc7',
        'metaTemplateId': '275af32e-bc40-45c2-85b7-afb1c0382653',
        'languages': ['2055'],
        'localizedName': '3 Example Word file',
        'templateGroupId': 1,
    }
    template_excel = {
        'id': '2574d08d-95ea-4639-beab-3103fe4c3bc8',
        'metaTemplateId': 'e31ca353-2ab1-4408-921b-a70ae2f57ad1',
        'languages': ['2055'],
        'localizedName': '2 Example Excel file',
        'templateGroupId': 2,
    }
    template_powerpoint = {
        'id': '2574d08d-95ea-4639-beab-3103fe4c3bc9',
        'metaTemplateId': 'a2c9b700-86cd-4481-a17f-533fe9c504a2',
        'languages': ['2055'],
        'localizedName': '1 Example Powerpoint presentation',
        'templateGroupId': 3,
    }

    def tearDown(self):
        # Tear down the singleton
        OneoffixxAPIClient.__metaclass__._instances.pop(OneoffixxAPIClient, None)
        super(BaseOneOffixxTestCase, self).tearDown()

    def mock_oneoffixx_api_client(self, template_groups=[], favorites=[]):
        api.portal.set_registry_record('protocol', u'mock', IOneoffixxSettings)
        api.portal.set_registry_record('hostname', u'nohost', IOneoffixxSettings)
        api.portal.set_registry_record('path_prefix', u'/foo', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'foobar', IOneoffixxSettings)

        access_token = {'access_token': 'all_may_enter'}
        template_library = {'datasources': [{'id': 1, 'isPrimary': True}]}
        organization_units = [{'id': 'fake-org-id'}]

        session = requests.Session()
        adapter = requests_mock.Adapter()
        adapter.register_uri('POST', 'mock://nohost/foo/ids/connect/token', text=json.dumps(access_token))
        adapter.register_uri('GET', 'mock://nohost/foo/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        adapter.register_uri('GET', 'mock://nohost/foo/webapi/api/v1/1/OrganizationUnits',
                             text=json.dumps(organization_units))
        adapter.register_uri(
            'GET',
            'mock://nohost/foo/webapi/api/v1/1/TemplateLibrary/TemplateGroups',
            text=json.dumps(template_groups),
        )
        adapter.register_uri(
            'GET',
            'mock://nohost/foo/webapi/api/v1/1/TemplateLibrary/TemplateFavorites',
            text=json.dumps(favorites),
        )
        session.mount('mock', adapter)

        credentials = {
            'client_id': 'foo',
            'client_secret': 'topsecret',
            'preshared_key': 'horribletruth',
        }

        return OneoffixxAPIClient(session, credentials)
