from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase


class TestRedirectToMainDossier(FunctionalTestCase):

    def setUp(self):
        super(TestRedirectToMainDossier, self).setUp()
        self.repo_root = create(Builder('repository_root'))
        self.repo = create(Builder('repository_root')
                           .titled(u'F\xfchrung')
                           .within(self.repo_root))
        self.dossier = create(Builder('dossier').within(self.repo))

    @browsing
    def test_redirects_to_main_dossier(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        task = create(Builder('task').within(self.dossier))
        document = create(Builder('document').within(self.dossier))

        browser.login().open(subdossier, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)

        browser.open(task, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)

        browser.open(document, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)

    @browsing
    def test_redirects_to_context_and_show_message_when_no_main_dossier_exists(self, browser):
        browser.login().open(self.repo, view='redirect_to_main_dossier')

        self.assertEquals(self.repo, browser.context)
        self.assertEquals(
            [u'The object `F\xfchrung` is not stored inside a dossier.'],
            error_messages())

    @browsing
    def test_handles_content_inside_a_subdossier_correctly(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        subsubdossier = create(Builder('dossier').within(subdossier))
        document = create(Builder('document').within(subsubdossier))

        browser.login().open(document, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)
