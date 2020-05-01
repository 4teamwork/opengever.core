from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2paths
from opengever.testing import SolrIntegrationTestCase


class TestDeleteActionInPrivateFolderTabbedViewsSolr(SolrIntegrationTestCase):

    @browsing
    def test_delete_action_is_displayed_for_owner(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_folder, view='tabbedview_view-dossiers')

        self.assertIn('Delete', browser.css('.actionMenuContent a').text)

    @browsing
    def test_delete_action_works_for_owner(self, browser):
        self.login(self.regular_user, browser)

        browser.open(
            self.private_folder,
            view='folder_delete_confirmation',
            data={'paths:list': obj2paths([self.private_dossier])},
            )

        browser.find('Delete').click()

        statusmessages.assert_message(u'Items successfully deleted.')

        with self.assertRaises(KeyError):
            self.assertIsNone(self.private_dossier)


class TestDeleteActionInPrivateFolderContentViews(IntegrationTestCase):

    @browsing
    def test_delete_action_is_displayed_for_owner_on_dossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_dossier)

        self.assertIn('Delete', browser.css('.actionMenuContent a span').text)

    @browsing
    def test_delete_action_works_for_owner_on_dossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_dossier)
        browser.find('Delete').click()
        browser.find('Delete').click()

        statusmessages.assert_message(u'Mein Dossier 1 has been deleted.')

        with self.assertRaises(KeyError):
            self.assertIsNone(self.private_dossier)

    @browsing
    def test_delete_action_is_displayed_for_owner_on_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_document)

        self.assertIn('Delete', browser.css('.actionMenuContent a span').text)

    @browsing
    def test_delete_action_works_for_owner_on_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_document)
        browser.find('Delete').click()
        browser.find('Delete').click()

        statusmessages.assert_message(u'Testdokum\xe4nt has been deleted.')

        with self.assertRaises(KeyError):
            self.assertIsNone(self.private_document)
