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
        template_groups = [
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532be',
                'localizedName': 'Word templates',
                'templates': [template_word],
            },
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532bf',
                'localizedName': 'Excel templates',
                'templates': [template_excel],
            },
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532c0',
                'localizedName': 'Powerpoint template folder',
                'templates': [template_powerpoint],
            },
        ]
        favorites = {
            'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532bd',
            'localizedName': 'Favorites',
            'templates': [],
        }
        session = requests.Session()
        adapter = requests_mock.Adapter()
        adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateGroups',
            text=json.dumps(template_groups),
        )
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateFavorites',
            text=json.dumps(favorites),
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

    @browsing
    def test_show_oneoffixx_templates_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates)
        expected_template_tabs = ['OneOffixx', 'Documents', 'Tasktemplate Folders']
        self.assertEqual(expected_template_tabs, browser.css('.formTab').text)

    @browsing
    def test_oneoffixx_templates_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates')
        expected_templates_table = [
            ['Title', 'Template group'],
            ['1 Example Powerpoint presentation', 'Powerpoint template folder'],
            ['2 Example Excel file', 'Excel templates'],
            ['3 Example Word file', 'Word templates'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())
        expected_css_classes = [
            ['1 Example Powerpoint presentation', ['icon-pptx']],
            ['2 Example Excel file', ['icon-xlsx']],
            ['3 Example Word file', ['icon-docx']],
        ]
        self.assertEqual(expected_css_classes, [[node.text, node.classes] for node in browser.css('td span')])

    @browsing
    def test_oneoffixx_templates_tab_sorting(self, browser):
        self.login(self.regular_user, browser)
        sort_query = {
            'sort': 'title',
            'dir': 'DESC',
            'ext': 'json',
            'tableType': 'extjs',
            'mode': 'json',
        }
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates', data=sort_query)
        expected_templates_table = [
            ['Title', 'Template group'],
            ['3 Example Word file', 'Word templates'],
            ['2 Example Excel file', 'Excel templates'],
            ['1 Example Powerpoint presentation', 'Powerpoint template folder'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())
        sort_query = {
            'sort': 'groupname',
            'dir': 'ASC',
            'ext': 'json',
            'tableType': 'extjs',
            'mode': 'json',
        }
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates', data=sort_query)
        expected_templates_table = [
            ['Title', 'Template group'],
            ['2 Example Excel file', 'Excel templates'],
            ['1 Example Powerpoint presentation', 'Powerpoint template folder'],
            ['3 Example Word file', 'Word templates'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())

    @browsing
    def test_oneoffixx_templates_tab_search(self, browser):
        self.login(self.regular_user, browser)
        post_query = {
            'ext': 'json',
            'tableType': 'extjs',
            'mode': 'json',
        }
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates?searchable_text=folder', data=post_query)
        expected_templates_table = [
            ['Title', 'Template group'],
            ['1 Example Powerpoint presentation', 'Powerpoint template folder'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates?searchable_text=word', data=post_query)
        expected_templates_table = [
            ['Title', 'Template group'],
            ['3 Example Word file', 'Word templates'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates?searchable_text=templates', data=post_query)
        expected_templates_table = [
            ['Title', 'Template group'],
            ['2 Example Excel file', 'Excel templates'],
            ['3 Example Word file', 'Word templates'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())
        browser.open(self.templates, view='tabbedview_view-oneoffixxtemplates?searchable_text=presentation', data=post_query)
        expected_templates_table = [
            ['Title', 'Template group'],
            ['1 Example Powerpoint presentation', 'Powerpoint template folder'],
        ]
        self.assertEqual(expected_templates_table, browser.css('table').first.lists())


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
        favorites = {'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532bd', 'localizedName': 'Favorites', 'templates': []}
        session = requests.Session()
        adapter = requests_mock.Adapter()
        adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateGroups',
            text=json.dumps(template_groups),
        )
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateFavorites',
            text=json.dumps(favorites),
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


class TestOneoffixxTemplateFavorites(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")

    def setUp(self):
        super(TestOneoffixxTemplateFavorites, self).setUp()
        api.portal.set_registry_record('baseurl', u'mock://nohost', IOneoffixxSettings)
        api.portal.set_registry_record('fake_sid', u'foobar', IOneoffixxSettings)

        access_token = {'access_token': 'all_may_enter'}
        template_library = [{'datasources': [{'id': 1}]}]
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
        template_groups = [
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532be',
                'localizedName': 'Word templates',
                'templates': [template_word],
            },
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532bf',
                'localizedName': 'Excel templates',
                'templates': [template_excel],
            },
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532c0',
                'localizedName': 'Powerpoint template folder',
                'templates': [template_powerpoint],
            },
        ]
        favorites = {
            'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532bd',
            'localizedName': 'Favorites',
            'templates': [template_powerpoint],
        }
        session = requests.Session()
        adapter = requests_mock.Adapter()
        adapter.register_uri('POST', 'mock://nohost/ids/connect/token', text=json.dumps(access_token))
        adapter.register_uri('GET', 'mock://nohost/webapi/api/v1/TenantInfo', text=json.dumps(template_library))
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateGroups',
            text=json.dumps(template_groups),
        )
        adapter.register_uri(
            'GET',
            'mock://nohost/webapi/api/v1/1/TemplateLibrary/TemplateFavorites',
            text=json.dumps(favorites),
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
        super(TestOneoffixxTemplateFavorites, self).tearDown()

    @browsing
    def test_oneoffixx_favorites_listed_as_a_category(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')
        expected_categories = [
            'All templates',
            'Favorites',
            'Word templates',
            'Excel templates',
            'Powerpoint template folder',
        ]
        self.assertEqual(expected_categories, browser.css('select option').text)

    @browsing
    def test_oneoffixx_favorites_not_duplicated_on_select_all(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')
        expected_options = [
            '3 Example Word file',
            '2 Example Excel file',
            '1 Example Powerpoint presentation',
        ]
        self.assertEqual(
            expected_options,
            [e.get('title') for e in browser.css('input[type=radio]')],
        )

    @browsing
    def test_oneoffixx_favorites_lists_only_favorites(self, browser):
        self.login(self.regular_user, browser)
        view = (
            'document_with_oneoffixx_template'
            '/++widget++form.widgets.template'
            '/ajax_render'
            '?form.widgets.template_group:list=c2ddc01a-befd-4e0d-b15f-f67025f532bd'
            '&form.widgets.template_group-empty-marker=1'
            '&form.widgets.template-empty-marker=1'
            '&form.widgets.title'
        )  # Do not add commas above, this is a string!
        browser.open(self.dossier, view=view, send_authenticator=True)
        expected_options = ['1 Example Powerpoint presentation']
        self.assertEqual(
            expected_options,
            [e.get('title') for e in browser.css('input[type=radio]')],
        )
