from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestLanguageToolPatch(IntegrationTestCase):

    @browsing
    def test_patch_returns_translated_error_message(self, browser):
        self.login(self.administrator, browser)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'de-ch'}
        data = {'reference_number_prefix': '1'}
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.empty_repofolder, data=json.dumps(data),
                         method='PATCH', headers=headers)

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(
            u'Eingaben sind ung\xfcltig', browser.json[u'translated_message'])

        self.assertEqual(
            {u'fields': [{
                u'field': u'reference_number',
                u'translated_message': u'Das Aktenzeichen 1 wird bereits verwendet.',
                u'type': u'ValidationError'}]},
            browser.json['additional_metadata'])
