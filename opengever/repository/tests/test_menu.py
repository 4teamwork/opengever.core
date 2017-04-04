from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import FunctionalTestCase


class TestRepositoryFolderFactoryMenu(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryFolderFactoryMenu, self).setUp()

    @browsing
    def test_businesscase_dossier_is_displayed_by_default(self, browser):
        repository_root = create(Builder('repository'))
        repository_folder = create(Builder('repository').within(repository_root))

        browser.login().visit(repository_folder)

        self.assertIn(
            'Business Case Dossier',
            factoriesmenu.addable_types())

    @browsing
    def test_businesscase_dossier_is_not_displayed_if_businesscase_dossiers_are_disallowed(self, browser):
        repository_root = create(Builder('repository'))
        repository_folder = create(Builder('repository')
                                   .within(repository_root)
                                   .having(allow_add_businesscase_dossier=False))

        browser.login().visit(repository_folder)

        self.assertNotIn(
            'Businesscase Dossier',
            factoriesmenu.addable_types())
