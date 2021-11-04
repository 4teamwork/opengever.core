from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestGeverErrorHandling(IntegrationTestCase):

    @browsing
    def test_validation_errors_are_extendend_with_translated_field_errors(self, browser):
        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(self.empty_repofolder, method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'reference_number_prefix': u'1'}))

        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {
                 u'fields': [
                     {u'field': u'reference_number',
                      u'translated_message': u'The reference_number 1 is already in use.',
                      u'type': u'ValidationError'}
                 ]},
             u'translated_message': u'Inputs not valid',
             u'message': u"[{'field': 'reference_number', 'message': u'msg_reference_already_in_use', 'error': 'ValidationError'}]"},
            browser.json)

    @browsing
    def test_errros_with_message_factory_messages_are_extended_with_translation(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.private_dossier, view='/@move',
                         data=json.dumps({"source": self.document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_docs_cant_be_moved_from_repo_to_private_repo',
             u'translated_message': u'Documents within the repository cannot be moved to the private repository.',
             u'type': u'Forbidden'},
            browser.json)
