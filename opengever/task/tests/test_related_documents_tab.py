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
            "Copy Items",
            "Send as email",
            "Checkout",
            "Cancel",
            "Export selection",
            "Move Items",
            "trashed",
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
            "Copy Items",
            "Attach selection",
            "Checkout",
            "Cancel",
            "Export selection",
            "Move Items",
            "trashed",
        ]
        self.assertEqual(expected_actions, browser.css(".actionMenu a").text)
