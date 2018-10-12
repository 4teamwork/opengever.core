from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.oneoffixx.api_client import OneoffixxAPIClient
from opengever.oneoffixx.exceptions import OneoffixxBackendException
from opengever.oneoffixx.exceptions import OneoffixxConfigurationException
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.testing import IntegrationTestCase
from plone import api
from zope.annotation.interfaces import IAnnotations
import json
import requests
import requests_mock


class TestCreateDocFromOneoffixxTemplate(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    def setUp(self):
        super(TestCreateDocFromOneoffixxTemplate, self).setUp()
        api.portal.set_registry_record('baseurl', u'mock://nohost', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'foobar', IOneoffixxSettings)

        access_token = {'access_token': 'all_may_enter'}
        template_library = [{'datasources': [{'id': 1}]}]
        template = {
            'id': '2574d08d-95ea-4639-beab-3103fe4c3bc7',
            'metaTemplateId': '275af32e-bc40-45c2-85b7-afb1c0382653',
            'languages': ['2055'],
            'localizedName': 'Example',
            'templateGroupId': 1,
        }
        template_groups = [{'templates': [template]}]

        session = requests.Session()
        adapter = requests_mock.Adapter()
        adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateGroups',
            text=json.dumps(template_groups),
        )
        session.mount('mock', adapter)

        credentials = {
            'client_id': 'foo',
            'client_secret': 'topsecret',
            'preshared_key': 'horribletruth',
        }

        OneoffixxAPIClient(session, credentials)

    def tearDown(self):
        api.portal.set_registry_record('baseurl', u'', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'', IOneoffixxSettings)
        # Tear down the singleton
        OneoffixxAPIClient.__metaclass__._instances.pop(OneoffixxAPIClient, None)
        super(TestCreateDocFromOneoffixxTemplate, self).tearDown()

    @browsing
    def test_document_creation_from_oneoffixx_template_creates_shadow_doc(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')

        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()

        self.assertEqual('document-state-shadow',
                         api.content.get_state(browser.context))
        self.assertTrue(browser.context.is_shadow_document())

    @browsing
    def test_retry_button_visible_on_shadow_doc(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')
        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()
        browser.open(browser.context, view='tabbedview_view-overview')
        self.assertEqual(['Oneoffixx retry'], browser.css('a.oc-checkout').text)

    @browsing
    def test_template_id_stored_in_annotations(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')

        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()

        annotations = IAnnotations(browser.context)
        self.assertEqual(node.get("value"), annotations['template-id'])

class TestCreateDocFromOneoffixxFilterTemplate(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    def setUp(self):
        super(TestCreateDocFromOneoffixxFilterTemplate, self).setUp()
        api.portal.set_registry_record('baseurl', u'mock://nohost', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'foobar', IOneoffixxSettings)

        access_token = {'access_token': 'all_may_enter'}
        template_library = [{'datasources': [{'id': 1}]}]
        valid_template = {
            'id': '2574d08d-95ea-4639-beab-3103fe4c3bc7',
            'metaTemplateId': '275af32e-bc40-45c2-85b7-afb1c0382653',
            'languages': ['2055'],
            'localizedName': 'Example',
            'templateGroupId': 1,
        }
        invalid_template = {
            'id': '826b692c-f8b6-404c-9cf0-0f585649daa8',
            'metaTemplateId': '153f1db5-a673-41a2-a0cb-f93792c6d1b0',
            'languages': ['2055'],
            'localizedName': 'Example',
            'templateGroupId': 1,
        }
        template_groups = [{'templates': [valid_template, invalid_template]}]

        session = requests.Session()
        adapter = requests_mock.Adapter()
        adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateGroups',
            text=json.dumps(template_groups),
        )
        session.mount('mock', adapter)

        credentials = {
            'client_id': 'foo',
            'client_secret': 'topsecret',
            'preshared_key': 'horribletruth',
        }

        OneoffixxAPIClient(session, credentials)

    def tearDown(self):
        api.portal.set_registry_record('baseurl', u'', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'', IOneoffixxSettings)
        # Tear down the singleton
        OneoffixxAPIClient.__metaclass__._instances.pop(OneoffixxAPIClient, None)
        super(TestCreateDocFromOneoffixxFilterTemplate, self).tearDown()

    @browsing
    def test_document_creation_from_oneoffixx_lists_only_whitelisted_template_types(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')
        self.assertFalse(browser.css("#form-widgets-template-826b692c-f8b6-404c-9cf0-0f585649daa8"))
        self.assertTrue(browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7"))


class TestCreateDocFromUnconfiguredOneoffixxTemplate(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    def setUp(self):
        super(TestCreateDocFromUnconfiguredOneoffixxTemplate, self).setUp()
        api.portal.set_registry_record('fake_sid', u'foobar', IOneoffixxSettings)

    def tearDown(self):
        api.portal.set_registry_record('fake_sid', u'', IOneoffixxSettings)
        # Tear down the singleton
        OneoffixxAPIClient.__metaclass__._instances.pop(OneoffixxAPIClient, None)
        super(TestCreateDocFromUnconfiguredOneoffixxTemplate, self).tearDown()

    @browsing
    def test_oneoffixx_form_errors_on_missing_config(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        browser.exception_bubbling = True
        # Do note this will not fail if you actually do have the config file!
        with self.assertRaises(OneoffixxConfigurationException):
            factoriesmenu.add('document_with_oneoffixx_template')


class TestCreateDocFromUnconfiguredOneoffixxFakeSIDTemplate(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    def tearDown(self):
        # Tear down the singleton
        OneoffixxAPIClient.__metaclass__._instances.pop(OneoffixxAPIClient, None)
        super(TestCreateDocFromUnconfiguredOneoffixxFakeSIDTemplate, self).tearDown()

    @browsing
    def test_oneoffixx_form_errors_on_missing_config(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        browser.exception_bubbling = True
        with self.assertRaises(OneoffixxConfigurationException):
            factoriesmenu.add('document_with_oneoffixx_template')


class TestCreateDocFromOneoffixxBackendFailuresTemplate(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    def setUp(self):
        super(TestCreateDocFromOneoffixxBackendFailuresTemplate, self).setUp()
        api.portal.set_registry_record('baseurl', u'mock://nohost', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'foobar', IOneoffixxSettings)

        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount('mock', self.adapter)

        self.credentials = {
            'client_id': 'foo',
            'client_secret': 'topsecret',
            'preshared_key': 'horribletruth',
        }

    def tearDown(self):
        api.portal.set_registry_record('baseurl', u'', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'', IOneoffixxSettings)
        # Tear down the singleton
        OneoffixxAPIClient.__metaclass__._instances.pop(OneoffixxAPIClient, None)

        # Reset the mock session
        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount('mock', self.adapter)

        super(TestCreateDocFromOneoffixxBackendFailuresTemplate, self).tearDown()

    def test_access_token_bad_return(self):
        self.adapter.register_uri('POST', 'mock://nohost/ids/connect/token', status_code=400)
        with self.assertRaises(OneoffixxBackendException):
            OneoffixxAPIClient(self.session, self.credentials)

    def test_access_token_no_token(self):
        access_token = {}
        self.adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        with self.assertRaises(OneoffixxBackendException):
            OneoffixxAPIClient(self.session, self.credentials)

    @browsing
    def test_template_library_bad_return(self, browser):
        access_token = {'access_token': 'all_may_enter'}
        self.adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        self.adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', status_code=400)
        OneoffixxAPIClient(self.session, self.credentials)

        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        browser.exception_bubbling = True
        with self.assertRaises(OneoffixxBackendException):
            factoriesmenu.add('document_with_oneoffixx_template')

    @browsing
    def test_template_groups_bad_return(self, browser):
        access_token = {'access_token': 'all_may_enter'}
        template_library = [{'datasources': [{'id': 1}]}]
        self.adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        self.adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        self.adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateGroups', status_code=400)
        OneoffixxAPIClient(self.session, self.credentials)

        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        browser.exception_bubbling = True
        with self.assertRaises(OneoffixxBackendException):
            factoriesmenu.add('document_with_oneoffixx_template')


class TestOneOffixxTemplateFeature(IntegrationTestCase):

    @browsing
    def test_doc_from_oneoffixx_template_available_if_oneoffixxtemplate_feature_enabled(self, browser):
        self.activate_feature("officeconnector-checkout")
        self.login(self.manager, browser)
        browser.open(self.dossier)

        self.assertEquals(
            ['Document',
             'document_with_template',
             'Task',
             'Add task from template',
             'Subdossier',
             'Participant'],
            factoriesmenu.addable_types())

        self.activate_feature("oneoffixx")
        browser.open(self.dossier)
        self.assertEquals(
            ['Document',
             'document_with_template',
             'document_with_oneoffixx_template',
             'Task',
             'Add task from template',
             'Subdossier',
             'Participant'],
            factoriesmenu.addable_types())
