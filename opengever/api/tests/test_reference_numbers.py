from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.repository.deleter import RepositoryDeleter
from opengever.repository.interfaces import IDuringRepositoryDeletion
from opengever.testing import IntegrationTestCase
from plone import api
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
import json


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

    @browsing
    def test_handles_deleted_repository_folder(self, browser):
        self.login(self.administrator, browser)

        alsoProvides(self.request, IDuringRepositoryDeletion)
        api.content.delete(obj=self.leaf_repofolder)
        noLongerProvides(self.request, IDuringRepositoryDeletion)

        browser.open(self.branch_repofolder,
                     view="@reference-numbers",
                     method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'active': False,
              u'prefix': u'1',
              u'title': None}],
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

    @browsing
    def test_unlocks_inactive_number_wich_is_used_by_removed_content(self, browser):
        self.login(self.administrator, browser)

        def get_numbers(obj):
            return browser.open(obj, view="@reference-numbers",
                                method='GET', headers=self.api_headers).json

        # Create a new repository with a reponumber 2
        repofolder = create(
            Builder('repository')
            .within(self.branch_repofolder)
            .having(title_de=u'Child', title_fr=u'Child', title_en=u'Child')
        )

        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'},
             {u'active': True,
              u'prefix': u'2',
              u'title': 'Child'}],
            get_numbers(self.branch_repofolder))

        # Removing it will set the number 2 to inactive
        RepositoryDeleter(repofolder).delete()

        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'},
             {u'active': False,
              u'prefix': u'2',
              u'title': None}],
            get_numbers(self.branch_repofolder))

        # And the number can be removed from the reference number manager
        browser.open(self.branch_repofolder,
                     view="@reference-numbers/2",
                     method='DELETE',
                     headers=self.api_headers)

        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            get_numbers(self.branch_repofolder))

        # Moving an existing repofolder (or a new one) to the number 2
        browser.open(
            self.leaf_repofolder, method='PATCH', headers=self.api_headers,
            data=json.dumps({'reference_number_prefix': '2'}))

        self.assertEqual(
            [{u'active': False,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'},
             {u'active': True,
              u'prefix': u'2',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            get_numbers(self.branch_repofolder))

        # And back to the previous value will inactivate the 2 again
        browser.open(
            self.leaf_repofolder, method='PATCH', headers=self.api_headers,
            data=json.dumps({'reference_number_prefix': '1'}))

        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'},
             {u'active': False,
              u'prefix': u'2',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            get_numbers(self.branch_repofolder))

        # And should be removeable again
        browser.open(self.branch_repofolder,
                     view="@reference-numbers/2",
                     method='DELETE',
                     headers=self.api_headers)

        self.assertEqual(
            [{u'active': True,
              u'prefix': u'1',
              u'title': u'Vertr\xe4ge und Vereinbarungen'}],
            get_numbers(self.branch_repofolder))
