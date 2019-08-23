from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
import json


class TestCopyPasteAPI(IntegrationTestCase):

    @browsing
    def test_copy_paste_document(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }

        with self.observe_children(self.empty_dossier) as children:
            browser.open(
                self.empty_dossier.absolute_url() + '/@copy',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        copy = children["added"].pop()
        self.assertEqual("copy of " + self.document.title, copy.title)
        self.assertEqual([{u'source': self.document.absolute_url(),
                           u'target': copy.absolute_url()}],
                         browser.json)

    @browsing
    def test_copy_paste_checked_out_document_is_forbidden(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }

        self.checkout_document(self.document)

        with browser.expect_http_error(500):
            browser.open(
                self.empty_dossier.absolute_url() + '/@copy',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual({u'message': u'Checked out documents cannot be copied.',
                          u'type': u'CopyError'},
                         browser.json)
