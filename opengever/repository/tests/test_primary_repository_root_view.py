from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.repository.browser.primary_repository_root import PrimaryRepositoryRoot
from opengever.testing import IntegrationTestCase


class TestPrimaryRepositoryRoot(IntegrationTestCase):

    @browsing
    def test_get_primary_repository_root(self, browser):
        self.login(self.administrator, browser=browser)

        view = PrimaryRepositoryRoot(self.portal, self.request)
        self.assertEqual(self.repository_root,
                         view.get_primary_repository_root())

        create(Builder('repository_root').titled(u'root1'))
        root17 = create(Builder('repository_root').titled(u'root17'))
        create(Builder('repository_root').titled(u'root2'))

        self.assertEqual(root17, view.get_primary_repository_root())

    @browsing
    def test_render_redirects_to_repository_root(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(view='primary_repository_root')
        self.assertEqual(self.repository_root.absolute_url(), browser.url)

        root2 = create(Builder('repository_root').titled(u'root2'))
        browser.open(view='primary_repository_root')
        self.assertEqual(root2.absolute_url(), browser.url)
