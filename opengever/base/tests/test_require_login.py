from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD


class TestRequireLoginScript(FunctionalTestCase):

    def setUp(self):
        super(TestRequireLoginScript, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .with_dummy_content())

    @browsing
    def test_require_login_redirects_to_came_from_if_already_logged_in(self, browser):
        browser.login().open(
            view='require_login',
            data={'came_from': self.document.absolute_url()})
        self.assertEqual(browser.url, self.document.absolute_url())

    @browsing
    def test_require_login_displays_login_form_and_redirecs_upon_login(self, browser):
        browser.open(
            view='require_login',
            data={'came_from': self.document.absolute_url()})
        self.assertEqual('http://nohost/plone/require_login', browser.url)

        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertEqual(browser.url, self.document.absolute_url())
