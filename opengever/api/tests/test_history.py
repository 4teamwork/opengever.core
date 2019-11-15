from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from plone import api
import json


class TestHistoryPatchEndpointForDocuments(IntegrationTestCase):

    @browsing
    def test_reverting_to_older_version(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)

        self.assertEqual('VERSION 1 DATA', self.document.file.data)

        browser.open(self.document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('VERSION 0 DATA', self.document.file.data)

    @browsing
    def test_reverting_to_older_version_creates_new_version(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)

        repo_tool = api.portal.get_tool('portal_repository')
        self.assertEqual(2, len(repo_tool.getHistory(self.document)))
        self.assertEqual(1, self.document.version_id)

        browser.open(self.document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(3, len(repo_tool.getHistory(self.document)))
        self.assertEqual(2, self.document.version_id)

    @browsing
    def test_reverting_to_older_version_does_not_revert_metadata(self, browser):
        self.login(self.regular_user, browser)

        self.document.title = "Title version 0"
        create_document_version(self.document, 0)
        self.document.title = "Title version 1"
        create_document_version(self.document, 1)

        self.assertEqual('Title version 1', self.document.title)

        browser.open(self.document,
                     view='@history',
                     data=json.dumps({"version": 0}),
                     method='PATCH',
                     headers=self.api_headers)

        self.assertEqual('Title version 1', self.document.title)

    @browsing
    def test_reverting_to_older_version_fails_when_document_checked_out(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)
        create_document_version(self.document, 1)
        self.checkout_document(self.document)

        self.assertEqual('VERSION 1 DATA', self.document.file.data)

        with browser.expect_http_error(401):
            browser.open(self.document,
                         view='@history',
                         data=json.dumps({"version": 0}),
                         method='PATCH',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Unauthorized()', u'type': u'Unauthorized'},
            browser.json)
        self.assertEqual('VERSION 1 DATA', self.document.file.data)

    @browsing
    def test_reverting_inexistant_version_fails(self, browser):
        self.login(self.regular_user, browser)

        create_document_version(self.document, 0)

        self.assertEqual('VERSION 0 DATA', self.document.file.data)

        with browser.expect_http_error(500):
            browser.open(self.document,
                         view='@history',
                         data=json.dumps({"version": 3}),
                         method='PATCH',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message':
                u"Retrieving of '<Document at {}>' failed. Version '3' "
                u"does not exist. ".format(self.document.absolute_url_path()),
             u'type': u'ArchivistRetrieveError'}, browser.json)
        self.assertEqual('VERSION 0 DATA', self.document.file.data)
