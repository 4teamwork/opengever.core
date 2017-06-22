from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase


class TestRepositoryFolderFactoryMenu(IntegrationTestCase):

    @browsing
    def test_businesscase_dossier_is_addable_by_default(self, browser):
        self.login(self.regular_user)
        browser.login(self.regular_user).open(self.leaf_repository)
        self.assertIn('Business Case Dossier', factoriesmenu.addable_types())

    @browsing
    def test_businesscase_dossier_is_not_addable_when_disallowed(self, browser):
        self.login(self.regular_user)
        self.leaf_repository.allow_add_businesscase_dossier = False
        browser.login(self.regular_user).open(self.leaf_repository)
        self.assertNotIn('Business Case Dossier', factoriesmenu.addable_types())
