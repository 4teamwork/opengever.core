from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestFileActionButtonTemplates(IntegrationTestCase):

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)


class TestFileActionButtonTemplatesWithBumblebee(IntegrationTestCase):
    features = (
        'bumblebee',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

    @browsing
    def test_bumblebee(self, browser):
        view = 'bumblebee-overlay-listing'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)


class TestFileActionButtonTemplatesWithOCAttach(IntegrationTestCase):
    features = (
        'officeconnector-attach',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)


class TestFileActionButtonTemplatesWithOCAttachAndBumblebee(IntegrationTestCase):
    features = (
        'bumblebee',
        'officeconnector-attach',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

    @browsing
    def test_bumblebee(self, browser):
        view = 'bumblebee-overlay-listing'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)


class TestFileActionButtonTemplatesWithOCCheckout(IntegrationTestCase):
    features = (
        'officeconnector-checkout',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)


class TestFileActionButtonTemplatesWithOCCheckoutAndBumblebee(IntegrationTestCase):
    features = (
        'bumblebee',
        'officeconnector-checkout',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Send as email',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

    @browsing
    def test_bumblebee(self, browser):
        view = 'bumblebee-overlay-listing'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)


class TestFileActionButtonTemplatesWithOCEverything(IntegrationTestCase):
    features = (
        'officeconnector-attach',
        'officeconnector-checkout',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'PDF Preview',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)


class TestFileActionButtonTemplatesWithOCEverythingAndBumblebee(IntegrationTestCase):
    features = (
        'bumblebee',
        'officeconnector-attach',
        'officeconnector-checkout',
        )

    @browsing
    def test_overview(self, browser):
        view = 'tabbedview_view-overview'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Checkout and edit',
            'Download copy',
            'Attach to email'
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email'
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = []
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email'
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        view = 'tooltip'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

    @browsing
    def test_dossier_documents_view(self, browser):
        view = 'tabbedview_view-documents'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        browser.open(self.dossier, view=view)
        actions = [
            'Create Task',
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            'trashed',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.dossier, view=view)
        actions = [
            u'More actions \u25bc',
            'Export as Zip',
            'Copy Items',
            'Attach selection',
            'Export selection',
            'Move Items',
            ]
        self.assertEqual(actions, browser.css('.tabbedview-action-list a').text)

    @browsing
    def test_bumblebee(self, browser):
        view = 'bumblebee-overlay-listing'

        self.login(self.dossier_responsible, browser)

        # Open Dossier
        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Edit metadata',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Edit metadata',
            'Checkout and edit',
            'Download copy',
            'Attach to email',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Inactive Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Resolved Dossier
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        # Document without file
        browser.open(self.document_without_file, view=view)
        actions = [
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)

        # Document with file
        browser.open(self.document, view=view)
        actions = [
            'Download copy',
            'Attach to email',
            'Open as PDF',
            'Open detail view',
            ]
        self.assertEqual(actions, browser.css('.file-action-buttons a').text)
