from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase


class TestTaskRelatedDocumentsTabWithoutOfficeconnector(SolrIntegrationTestCase):

    features = ("!officeconnector-attach",)

    @browsing
    def test_attach_action_on_related_documents_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy")
        expected_actions = [
            u"More actions \u25bc",
            "Export as Zip",
            "Copy items",
            "Send as email",
            "Check out",
            "Cancel",
            "Export selection",
            "Move items",
            "Move to trash",
        ]
        self.assertEqual(expected_actions, browser.css(".actionMenu a").text)


class TestTaskRelatedDocumentsTabWithOfficeconnector(SolrIntegrationTestCase):

    features = ("officeconnector-attach",)

    @browsing
    def test_attach_action_on_related_documents_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy")
        expected_actions = [
            u"More actions \u25bc",
            "Export as Zip",
            "Copy items",
            "Attach to email",
            "Check out",
            "Cancel",
            "Export selection",
            "Move items",
            "Move to trash",
        ]
        self.assertEqual(expected_actions, browser.css(".actionMenu a").text)
