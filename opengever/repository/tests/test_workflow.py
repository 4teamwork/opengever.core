from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized


class TestRepositoryWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryWorkflow, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.repository_root))

    @browsing
    def test_list_folder_contents_on_repository_is_not_available_for_adminstrators(self, browser):
        self.grant('Administrator')

        with self.assertRaises(Unauthorized):
            browser.login().open(self.repository, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repository_is_available_for_managers(self, browser):
        self.grant('Manager')

        browser.login().open(self.repository, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repositoryroot_is_not_available_for_adminstrators(self, browser):
        self.grant('Administrator')

        with self.assertRaises(Unauthorized):
            browser.login().open(self.repository_root, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repositoryroot_is_available_for_managers(self, browser):
        self.grant('Manager')

        browser.login().open(self.repository_root, view='folder_contents')
