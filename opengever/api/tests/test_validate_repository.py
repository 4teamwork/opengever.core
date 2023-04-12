from base64 import b64encode
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_string
import json


class TestValidateRepository(IntegrationTestCase):

    @browsing
    def test_validate_repository_without_file_raises_bad_request(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal.absolute_url() + '/@validate-repository',
                         method='POST',
                         headers={'Accept': 'application/json'})
        self.assertEqual({u'message': u'Missing file.', u'type': u'BadRequest'},
                         browser.json)

    @browsing
    def test_valid_repository_validation_succeeds(self, browser):
        self.login(self.regular_user, browser)
        file_data = resource_string('opengever.bundle.tests',
                                    'assets/basic_repository.xlsx')
        data = json.dumps({
            "file": {
                "filename": "ordnungssystem.xlsx",
                "data": b64encode(file_data),
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        })
        browser.open(self.portal.absolute_url(), view='/@validate-repository',
                     method='POST', headers=self.api_headers, data=data)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_validating_repository_with_missing_parent_position_raises_bad_request(self, browser):
        self.login(self.regular_user, browser)
        file_data = resource_string('opengever.bundle.tests',
                                    'assets/invalid_repository_missing_parent.xlsx')
        data = json.dumps({
            "file": {
                "filename": "ordnungssystem.xlsx",
                "data": b64encode(file_data),
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        })
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal.absolute_url(), view='/@validate-repository',
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(
            {u'message': u'Parent position 0.0 for 0.0.0 does not exist!',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_validating_repository_not_satisfying_schema_raises_bad_request(self, browser):
        self.login(self.regular_user, browser)
        file_data = resource_string('opengever.bundle.tests',
                                    'assets/invalid_repository_schema_not_satisfied.xlsx')
        data = json.dumps({
            "file": {
                "filename": "ordnungssystem.xlsx",
                "data": b64encode(file_data),
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        })
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal.absolute_url(), view='/@validate-repository',
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(u'BadRequest', browser.json['type'])
        self.assertEqual(u'Inputs not valid', browser.json['translated_message'])
        self.assertEqual(
            [{u'field': u'retention_period',
              u'item_title': u'F\xfchrung',
              u'translated_message': u'50 is not one of [None, 5, 10, 15, 20, 25]',
              u'type': u'ValidationError'},
             {u'field': u'archival_value',
              u'item_title': u'Gemeinderecht',
              u'translated_message': (u"'Keine' is not one of [None, u'unchecked', u'prompt', u'archival worthy',"
                                      u" u'not archival worthy', u'archival worthy with sampling']"),
              u'type': u'ValidationError'}],
            browser.json['additional_metadata']['fields'])
