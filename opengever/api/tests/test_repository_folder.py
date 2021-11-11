from ftw.testbrowser import browsing
from opengever.base.interfaces import IReferenceNumberPrefix as PrefixAdapter
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.testing import IntegrationTestCase
import json


class TestRepositoryFolderPost(IntegrationTestCase):

    @browsing
    def test_post_validates_reference_number_prefix(self, browser):
        self.login(self.administrator, browser)
        self.assertFalse(PrefixAdapter(
            self.repository_root).is_valid_number("1"))

        data = {
            "@type": "opengever.repository.repositoryfolder",
            "title_de": "Folder",
            "title_fr": u"F\xf6lder",
            "title_en": "Folder",
            "reference_number_prefix": "1"
        }
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.repository_root, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(
            u'Inputs not valid', browser.json[u'translated_message'])
        self.assertEqual(
            {u'fields': [
                {u'field': u'reference_number',
                 u'translated_message': u'The reference_number 1 is already in use.',
                 u'type': u'ValidationError'}]},
            browser.json[u'additional_metadata'])


class TestRepositoryFolderPatch(IntegrationTestCase):

    @browsing
    def test_patch_validates_changed_reference_number_prefix(self, browser):
        self.login(self.administrator, browser)
        self.assertFalse(PrefixAdapter(self.repository_root)
                         .is_valid_number("1"))

        data = {
            "reference_number_prefix": "1"
        }
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.empty_repofolder, data=json.dumps(data),
                         method='PATCH', headers=self.api_headers)

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(
            u'Inputs not valid', browser.json[u'translated_message'])
        self.assertEqual(
            {u'fields': [
                {u'field': u'reference_number',
                 u'translated_message': u'The reference_number 1 is already in use.',
                 u'type': u'ValidationError'}]},
            browser.json[u'additional_metadata'])

    @browsing
    def test_patch_allows_unchanged_reference_number_prefix(self, browser):
        self.login(self.administrator, browser)

        current_number = IReferenceNumberPrefix(
            self.empty_repofolder).reference_number_prefix
        self.assertTrue(PrefixAdapter(self.repository_root).is_valid_number(
            current_number, self.empty_repofolder))
        data = {
            "reference_number_prefix": current_number
        }
        browser.open(self.empty_repofolder, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertEqual(current_number, IReferenceNumberPrefix(
            self.empty_repofolder).reference_number_prefix)
