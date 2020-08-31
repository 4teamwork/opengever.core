from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import IntegrationTestCase


class TestRedirectToMainDossier(IntegrationTestCase):

    @browsing
    def test_redirects_to_main_dossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.subdossier, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)

        browser.open(self.task, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)

        browser.open(self.document, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)

    @browsing
    def test_redirects_to_context_and_show_message_when_no_main_dossier_exists(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, view='redirect_to_main_dossier')

        self.assertEquals(self.leaf_repofolder, browser.context)
        self.assertEquals(
            [u'The object `1.1. Vertr\xe4ge und Vereinbarungen` is not stored inside a dossier.'],
            error_messages())

    @browsing
    def test_handles_content_inside_a_subdossier_correctly(self, browser):
        self.login(self.regular_user, browser)
        browser.login().open(self.subsubdocument, view='redirect_to_main_dossier')
        self.assertEquals(self.dossier, browser.context)
