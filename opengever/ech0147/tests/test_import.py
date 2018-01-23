from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import obj2brain
import os.path


def get_path(name):
    return os.path.join(os.path.dirname(__file__), 'data', name)


class TestImport(IntegrationTestCase):

    @browsing
    def test_actions_menu_doesnt_contain_ech0147_import_if_disabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder)
        actions = browser.css(
            '#plone-contentmenu-actions .actionMenuContent .subMenuTitle'
            ).normalized_text()
        self.assertNotIn('eCH-0147 Import', actions)

    @browsing
    def test_actions_menu_contains_ech0147_import(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder)
        actions = browser.css(
            '#plone-contentmenu-actions .actionMenuContent .subMenuTitle'
            ).normalized_text()
        self.assertIn('eCH-0147 Import', actions)

    @browsing
    def test_import_dossier_returns_404_if_disabled(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=404):
            browser.open(self.leaf_repofolder, view='ech0147_import')

    @browsing
    def test_import_dossier_creates_dossier(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='ech0147_import')
        with open(get_path('message.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        dossier = self.leaf_repofolder.objectValues()[-1]
        self.assertEqual(dossier.Title(), 'My eCH Dossier')

    @browsing
    def test_import_dossier_with_invalid_zip_displays_error(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='ech0147_import')
        with open(get_path('archive.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        self.assertIn('Invalid message. Missing message.xml', browser.contents)

    @browsing
    def test_import_dossier_with_minimal_set_of_metadata(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='ech0147_import')
        with open(get_path('message_min.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        dossier = self.leaf_repofolder.objectValues()[-1]
        self.assertEqual(dossier.Title(), 'Neubau Schwimmbad 50m')

    @browsing
    def test_import_dossier_with_full_set_of_metadata(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='ech0147_import')
        with open(get_path('message_full.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        dossier = self.leaf_repofolder.objectValues()[-1]
        self.assertEqual(dossier.Title(), 'Neubau Schwimmbad 50m')

    @browsing
    def test_import_toplevel_documents_in_dossier(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='ech0147_import')
        with open(get_path('message_docs_only.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        docs = self.dossier.objectValues()[-2:]
        self.assertEqual(docs[0].Title(), 'Kaufvertrag')
        self.assertEqual(docs[1].Title(), 'Grundrissplan')

        self.assertIsNotNone(obj2brain(docs[0]).bumblebee_checksum)

    @browsing
    def test_import_toplevel_documents_in_repofolder_displays_error(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='ech0147_import')
        with open(get_path('message_docs_only.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        self.assertIn('This message contains toplevel documents.', browser.contents)

    @browsing
    def test_import_invalid_message_displays_error(self, browser):
        self.activate_feature('ech0147-import')
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='ech0147_import')
        with open(get_path('message_invalid.zip')) as file_:
            browser.forms['form'].fill({
                'File': file_,
            }).submit()
        self.assertIn('Invalid content.', browser.contents)
