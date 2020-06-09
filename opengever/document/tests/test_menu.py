from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.testing import IntegrationTestCase


class TestActionMenu(IntegrationTestCase):

    @browsing
    def test_copy_unavailable_for_checked_out_document(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document)
        self.assertIn('Copy Item', editbar.menu_options('Actions'))

        self.checkout_document(self.document)
        browser.open(self.document)
        self.assertNotIn('Copy Item', editbar.menu_options('Actions'))

    @browsing
    def test_delete_available_for_templates(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.normal_template)
        self.assertIn('Delete', editbar.menu_options('Actions'))

        self.login(self.manager, browser)
        browser.open(self.normal_template)
        self.assertIn('Delete', editbar.menu_options('Actions'))

        self.login(self.dossier_responsible, browser)
        browser.open(self.normal_template)
        self.assertIn('Delete', editbar.menu_options('Actions'))
