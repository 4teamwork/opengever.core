from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestUploadStructure(IntegrationTestCase):

    @browsing
    def test_upload_structure(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'files': ['folder/file.txt', 'folder/subfolder/file2.txt']
        }
        response = browser.open(
            "{}/@upload-structure".format(self.leaf_repofolder.absolute_url()),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {u'items': {
                u'folder': {
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'relative_path': u'folder',
                    u'items': {
                        u'file.txt': {
                            u'@type': u'opengever.document.document',
                            u'relative_path': u'folder/file.txt'},
                        u'subfolder': {
                            u'@type': u'opengever.dossier.businesscasedossier',
                            u'relative_path': u'folder/subfolder',
                            u'items': {
                                u'file2.txt': {
                                    u'@type': u'opengever.document.document',
                                    u'relative_path': u'folder/subfolder/file2.txt'}
                                }
                            }
                        }
                    }
                },
             u'max_container_depth': 2,
             u'items_total': 4},
            browser.json)

    @browsing
    def test_upload_structure_respects_leading_slash(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'files': ['/folder/file.txt']
        }
        response = browser.open(
            "{}/@upload-structure".format(self.leaf_repofolder.absolute_url()),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {u'items': {
                u'folder': {
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'relative_path': u'/folder',
                    u'items': {
                        u'file.txt': {
                            u'@type': u'opengever.document.document',
                            u'relative_path': u'/folder/file.txt'},
                        }
                    }
                },
             u'max_container_depth': 1,
             u'items_total': 2},
            browser.json)

    @browsing
    def test_upload_structure_requires_files_list(self, browser):
        self.login(self.regular_user, browser)

        payload = {}
        with browser.expect_http_error(code=400):
            browser.open("{}/@upload-structure".format(self.leaf_repofolder.absolute_url()),
                         data=json.dumps(payload),
                         method='POST',
                         headers=self.api_headers)
        self.assertEqual(
            {u'message': u"Property 'files' is required", u'type': u'BadRequest'},
            browser.json)
