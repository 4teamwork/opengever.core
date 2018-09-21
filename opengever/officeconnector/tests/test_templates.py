from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestFileActionButtonTemplates(IntegrationTestCase):

    features = (
        '!officeconnector-attach',
        '!officeconnector-checkout',
    )

    @browsing
    def test_overview_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_overview_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_tooltip_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_dossier_documents_view_open(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_inactive(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_resolved(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)


class TestFileActionButtonTemplatesWithBumblebee(IntegrationTestCase):

    features = (
        '!officeconnector-attach',
        '!officeconnector-checkout',
        'bumblebee',
    )

    @browsing
    def test_overview_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_overview_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_tooltip_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_dossier_documents_view_open(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_inactive(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_resolved(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_bumblebee_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_bumblebee_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)


class TestFileActionButtonTemplatesWithOCAttach(IntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'officeconnector-attach',
    )

    @browsing
    def test_overview_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_overview_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_overview_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_tooltip_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_tooltip_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_tooltip_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_dossier_documents_view_open(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertIn('Attach selection', actions)
        self.assertIn('Checkout', actions)
        self.assertNotIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_inactive(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertNotIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_resolved(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertNotIn('Send as email', actions)


class TestFileActionButtonTemplatesWithOCAttachAndBumblebee(IntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'bumblebee',
        'officeconnector-attach',
    )

    @browsing
    def test_overview_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_overview_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_overview_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_tooltip_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_tooltip_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_tooltip_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_dossier_documents_view_open(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertIn('Attach selection', actions)
        self.assertIn('Checkout', actions)
        self.assertNotIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_inactive(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertNotIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_resolved(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertNotIn('Send as email', actions)

    @browsing
    def test_bumblebee_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertNotIn('javascript:', checkout_url)

    @browsing
    def test_bumblebee_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)

    @browsing
    def test_bumblebee_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

        attach_url = browser.css('.function-attach')[0].get('href')
        self.assertIn('javascript:', attach_url)


class TestFileActionButtonTemplatesWithOCCheckout(IntegrationTestCase):

    features = (
        '!officeconnector-attach',
        'officeconnector-checkout',
    )

    @browsing
    def test_overview_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertIn('javascript:', checkout_url)

    @browsing
    def test_overview_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertIn('javascript:', checkout_url)

    @browsing
    def test_tooltip_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_dossier_documents_view_open(self, browser):
        self.login(self.regular_user, browser)

        # Open Dossier
        browser.open(self.dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_inactive(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_resolved(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)


class TestFileActionButtonTemplatesWithOCCheckoutAndBumblebee(IntegrationTestCase):

    features = (
        '!officeconnector-attach',
        'bumblebee',
        'officeconnector-checkout',
    )

    @browsing
    def test_overview_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertIn('javascript:', checkout_url)

    @browsing
    def test_overview_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_overview_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertIn('javascript:', checkout_url)

    @browsing
    def test_tooltip_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_tooltip_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tooltip')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_dossier_documents_view_open(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_inactive(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_dossier_documents_view_resolved(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_dossier, view='tabbedview_view-documents')

        actions = browser.css('.tabbedview-action-list a').text
        self.assertNotIn('Attach selection', actions)
        self.assertNotIn('Checkout', actions)
        self.assertIn('Send as email', actions)

    @browsing
    def test_bumblebee_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = None

        browser.open(self.document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertIn('Checkout and edit', actions)

        checkout_url = browser.css('.function-edit')[0].get('href')
        self.assertIn('javascript:', checkout_url)

    @browsing
    def test_bumblebee_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        browser.open(self.inactive_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.inactive_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        browser.open(self.expired_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)

    @browsing
    def test_bumblebee_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='bumblebee-overlay-listing')

        actions = browser.css('.file-action-buttons a').text
        self.assertNotIn('Attach to email', actions)
        self.assertNotIn('Checkout and edit', actions)
