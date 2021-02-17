from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
import json


class TestCopyPasteAPI(IntegrationTestCase):

    @browsing
    def test_copy_renames_id(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.subdossier.absolute_url(),
        }

        browser.open(
            self.leaf_repofolder.absolute_url() + '/@copy',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers,
        )

        target_id = browser.json[0][u'target'].split('/')[-1]
        self.assertNotEqual(target_id, 'copy_of_' + self.subdossier.id)

        target = self.leaf_repofolder[target_id]
        self.assertEqual(
            set(target.objectIds()) & set(self.subdossier.objectIds()), set())

    @browsing
    def test_copy_renames_title_if_copied_to_same_container(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url() + '/@copy',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        copy = children["added"].pop()
        self.assertEqual("Copy of " + self.document.title, copy.title)
        self.assertEqual([{u'source': self.document.absolute_url(),
                           u'target': copy.absolute_url()}],
                         browser.json)

    @browsing
    def test_copy_updates_creator(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }
        browser.open(
            self.dossier.absolute_url() + '/@copy',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers,
        )

        target_id = browser.json[0][u'target'].split('/')[-1]
        target = self.dossier[target_id]
        self.assertEqual(target.Creator(), self.regular_user.getId())

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
