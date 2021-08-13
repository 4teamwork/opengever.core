from ftw.testbrowser import browsing
from opengever.base.adapters import ReferenceNumberPrefixAdpater
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


class TestReferenceNumbersDelete(IntegrationTestCase):

    @browsing
    def test_raises_when_number_is_missing(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_http_error(400):
            browser.open(self.branch_repofolder,
                         view="@reference-numbers",
                         method='DELETE',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Must supply a reference number as URL path parameter.',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_raises_when_number_is_still_in_use(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_http_error(400):
            browser.open(self.branch_repofolder,
                         view="@reference-numbers/1",
                         method='DELETE',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Number still in use.',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_unlocks_inactive_number(self, browser):
        self.login(self.administrator, browser)

        # move repo1 to prefix 3 which leaves prefix 1 unused
        manager = ReferenceNumberPrefixAdpater(self.branch_repofolder)
        manager.set_number(self.leaf_repofolder, 3)

        browser.open(self.branch_repofolder,
                     view="@reference-numbers",
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'active': False,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'},
             {u'active': True,
              u'prefix': u'3',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            browser.json)

        browser.open(self.branch_repofolder,
                     view="@reference-numbers/1",
                     method='DELETE',
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.branch_repofolder,
                     view="@reference-numbers",
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'active': True,
              u'prefix': u'3',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            browser.json)
