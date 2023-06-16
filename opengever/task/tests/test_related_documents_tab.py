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


class TestTaskRelatedDocumentsTab(SolrIntegrationTestCase):

    def setUp(self):
        super(TestTaskRelatedDocumentsTab, self).setUp()

        self.login(self.regular_user)
        self.set_related_items(
            self.task, [self.document, self.mail_eml])

    @browsing
    def test_shows_contained_and_related_documents(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy")

        self.assertEqual(
            [self.taskdocument.title,
             self.document.title,
             self.mail_eml.title],
            [r.get('Title') for r in browser.css('.listing').first.dicts()])

    @browsing
    def test_respects_sorting(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy",
                     data={'sort': 'sortable_title'})

        self.assertEqual(
            [u'Die B\xfcrgschaft',
             'Feedback zum Vertragsentwurf',
             u'Vertr\xe4gsentwurf'],
            [r.get('Title') for r in browser.css('.listing').first.dicts()])

        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy",
                     data={'sort': 'sortable_title', 'dir': 'DESC'})
        self.assertEqual(
            [u'Vertr\xe4gsentwurf',
             'Feedback zum Vertragsentwurf',
             u'Die B\xfcrgschaft'],
            [r.get('Title') for r in browser.css('.listing').first.dicts()])

    @browsing
    def test_supports_sorting_on_date(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy",
                     data={'sort': 'document_date'})
        self.assertEqual(
            ['01.01.1999', '03.01.2010', '31.08.2016'],
            [r.get('Document date') for r in browser.css('.listing').first.dicts()])

        browser.open(self.task, view="tabbedview_view-relateddocuments-proxy",
                     data={'sort': 'document_date', 'dir':'DESC'})
        self.assertEqual(
            ['31.08.2016', '03.01.2010', '01.01.1999'],
            [r.get('Document date') for r in browser.css('.listing').first.dicts()])
