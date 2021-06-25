from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestMove(IntegrationTestCase):

    def setUp(self):
        super(TestMove, self).setUp()

    @browsing
    def test_regular_user_can_move_document(self, browser):
        self.login(self.regular_user, browser)
        doc_id = self.document.getId()
        browser.open(
            self.subdossier.absolute_url() + '/@move',
            data=json.dumps({"source": self.document.absolute_url()}),
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, self.subdossier)

    @browsing
    def test_move_document_within_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        doc_id = self.dossiertemplatedocument.getId()
        browser.open(
            self.templates, view='@move',
            data=json.dumps({"source": self.dossiertemplatedocument.absolute_url()}),
            method='POST', headers=self.api_headers,
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, self.templates)

    @browsing
    def test_document_within_repository_cannot_be_moved_to_templates(self, browser):
        self.login(self.administrator, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.templates, view='/@move',
                         data=json.dumps({"source": self.document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual({u'type': u'Forbidden', u'message':
                          u'Documents within the repository cannot be moved to the templates.'},
                         browser.json)

    @browsing
    def test_move_document_within_private_folder_is_possible(self, browser):
        self.login(self.regular_user, browser)
        dossier = create(
            Builder('private_dossier')
            .within(self.private_folder))

        doc_id = self.private_document.getId()

        browser.open(
            dossier, view='@move',
            data=json.dumps({"source": self.private_document.absolute_url()}),
            method='POST', headers=self.api_headers,
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, dossier)

    @browsing
    def test_document_within_repository_cannot_be_moved_to_private_dossier(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.private_dossier, view='/@move',
                         data=json.dumps({"source": self.document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'Forbidden', u'message':
             u'Documents within the repository cannot be moved to the private repository.'},
            browser.json)
