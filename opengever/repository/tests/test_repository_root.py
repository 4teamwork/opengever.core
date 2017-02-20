from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase


class TestRepositoryRoot(FunctionalTestCase):

    @browsing
    def test_adding(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open()
        factoriesmenu.add('RepositoryRoot')
        browser.fill({'Title': 'RepositoryRoot'}).save()

        self.assertTrue(IRepositoryRoot.providedBy(browser.context))

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        browser.login().open()

        self.grant('Administrator')
        browser.reload()
        self.assertNotIn(
            'RepositoryRoot',
            factoriesmenu.addable_types()
            )

        self.grant('Manager')
        browser.reload()
        self.assertIn(
            'RepositoryRoot',
            factoriesmenu.addable_types()
            )

    def test_repository_root_name_from_title(self):
        root = create(Builder('repository_root').having(title_de=u'Foob\xe4r'))
        self.assertEqual('foobar', root.getId())
