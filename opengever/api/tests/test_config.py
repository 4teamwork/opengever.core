from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestConfig(IntegrationTestCase):

    def setUp(self):
        super(TestConfig, self).setUp()

    @browsing
    def test_config_contains_id(self, browser):
        self.login(self.administrator, browser)
        url = self.portal.absolute_url() + '/@config'
        browser.open(url, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'@id'), url)

    @browsing
    def test_config_contains_features(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'features'),
            {
                u'activity': False,
                u'contacts': False,
                u'doc_properties': False,
                u'dossier_templates': False,
                u'ech0147_export': False,
                u'ech0147_import': False,
                u'meetings': False,
                u'officeatwork': False,
                u'officeconnector_attach': False,
                u'officeconnector_checkout': False,
                u'preview': False,
                u'preview_open_pdf_in_new_window': False,
                u'repositoryfolder_documents_tab': True,
                u'repositoryfolder_tasks_tab': True,
                u'solr': False,
                u'word_meetings': False,
                u'workspace': False,
            })

    @browsing
    def test_config_contains_max_subdossier_depth(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'max_dossier_levels'), 2)

    @browsing
    def test_config_contains_max_repository_depth(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.portal.absolute_url() + '/@config',
                     headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'max_repositoryfolder_levels'), 3)
