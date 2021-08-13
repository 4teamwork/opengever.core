from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestReferenceNumbersGet(IntegrationTestCase):

    @browsing
    def test_get_reference_numbers_on_repository_folder(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder,
                     view="@reference-numbers",
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            browser.json)

    @browsing
    def test_get_reference_numbers_on_repository_root(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.repository_root,
                     view="@reference-numbers",
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'F\xfchrung'},
             {u'active': True,
              u'prefix': u'2',
              u'title': u'Rechnungspr\xfcfungskommission'},
             {u'active': True,
              u'prefix': u'3',
              u'title': u'Spinn\xe4nnetzregistrar'}],
            browser.json)
