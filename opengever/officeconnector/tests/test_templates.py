from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from plone import api

import transaction


class TestOCTemplatesDossierOpenWithoutFile(FunctionalTestCase):
    """Test templates on documents for OfficeConnector compatibility.

    Dossier: open
    Document: without file
    """

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOCTemplatesDossierOpenWithoutFile, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier').within(self.repo))
        self.document = create(Builder('document').within(self.dossier))

    @browsing
    def test_overview(self, browser):
        browser.login()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        browser.login()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_bumblebee(self, browser):
        browser.login()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_tabbed(self, browser):
        browser.login()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))


class TestOCTemplatesDossierInactiveWithoutFile(FunctionalTestCase):
    """Test templates on documents for OfficeConnector compatibility.

    Dossier: inactive
    Document: without file
    """

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOCTemplatesDossierInactiveWithoutFile, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .in_state('dossier-state-inactive'))
        self.document = create(Builder('document').within(self.dossier))

    @browsing
    def test_overview(self, browser):
        browser.login()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        browser.login()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_bumblebee(self, browser):
        browser.login()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_tabbed(self, browser):
        browser.login()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))


class TestOCTemplatesDossierResolvedWithoutFile(FunctionalTestCase):
    """Test templates on documents for OfficeConnector compatibility.

    Dossier: resolved
    Document: without file
    """

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOCTemplatesDossierResolvedWithoutFile, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .in_state('dossier-state-resolved'))
        self.document = create(Builder('document').within(self.dossier))

    @browsing
    def test_overview(self, browser):
        browser.login()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_tooltip(self, browser):
        browser.login()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_bumblebee(self, browser):
        browser.login()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_tabbed(self, browser):
        browser.login()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))


class TestOCTemplatesDossierOpenWithFile(FunctionalTestCase):
    """Test templates on documents for OfficeConnector compatibility.

    Dossier: open
    Document: with file
    """

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOCTemplatesDossierOpenWithFile, self).setUp()

        self.root = create(Builder('repository_root'))

        self.repo = create(Builder('repository')
                           .within(self.root))

        self.dossier = create(Builder('dossier')
                              .within(self.repo))

        self.document = create(Builder('document')
                               .within(self.dossier)
                               .attach_file_containing(bumblebee_asset(
                                   'example.docx').bytes(),
                                   u'example.docx'))

    @browsing
    def test_overview(self, browser):
        browser.login()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Checkout and edit',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn(self.document.absolute_url() + '/editing_document',
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Checkout and edit',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        self.assertIn(self.document.absolute_url() + '/editing_document',
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Checkout and edit',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorCheckout('",
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Checkout and edit',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        self.assertIn("javascript:officeConnectorCheckout('",
                      browser.css('a.function-edit')[1].get('href'))

    @browsing
    def test_tooltip(self, browser):
        browser.login()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Checkout and edit',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn(self.document.absolute_url() + '/editing_document',
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Checkout and edit',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        self.assertIn(self.document.absolute_url() + '/editing_document',
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Checkout and edit',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorCheckout('",
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Checkout and edit',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        self.assertIn("javascript:officeConnectorCheckout('",
                      browser.css('a.function-edit')[1].get('href'))

    @browsing
    def test_bumblebee(self, browser):
        browser.login()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Checkout and edit',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn(self.document.absolute_url() + '/editing_document',
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Checkout and edit',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        self.assertIn(self.document.absolute_url() + '/editing_document',
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Checkout and edit',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorCheckout('",
                      browser.css('a.function-edit')[1].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Checkout and edit',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        self.assertIn("javascript:officeConnectorCheckout('",
                      browser.css('a.function-edit')[1].get('href'))

    @browsing
    def test_tabbed(self, browser):
        browser.login()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual(['Create Task',
                          u'More actions \u25bc',
                          'Copy Items',
                          'Checkout',
                          'Cancel',
                          'Checkin with comment',
                          'Checkin without comment',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'trashed',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))


class TestOCTemplatesDossierInactiveWithFile(FunctionalTestCase):
    """Test templates on documents for OfficeConnector compatibility.

    Dossier: inactive
    Document: with file
    """

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOCTemplatesDossierInactiveWithFile, self).setUp()

        self.root = create(Builder('repository_root'))

        self.repo = create(Builder('repository')
                           .within(self.root))

        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .in_state('dossier-state-inactive'))

        self.document = create(Builder('document')
                               .within(self.dossier)
                               .attach_file_containing(bumblebee_asset(
                                   'example.docx').bytes(),
                                   u'example.docx'))

    @browsing
    def test_overview(self, browser):
        browser.login()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

    @browsing
    def test_tooltip(self, browser):
        browser.login()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

    @browsing
    def test_bumblebee(self, browser):
        browser.login()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

    @browsing
    def test_tabbed(self, browser):
        browser.login()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))


class TestOCTemplatesDossierResolvedWithFile(FunctionalTestCase):
    """Test templates on documents for OfficeConnector compatibility.

    Dossier: resolved
    Document: with file
    """

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOCTemplatesDossierResolvedWithFile, self).setUp()

        self.root = create(Builder('repository_root'))

        self.repo = create(Builder('repository')
                           .within(self.root))

        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .in_state('dossier-state-resolved'))

        self.document = create(Builder('document')
                               .within(self.dossier)
                               .attach_file_containing(bumblebee_asset(
                                   'example.docx').bytes(),
                                   u'example.docx'))

    @browsing
    def test_overview(self, browser):
        browser.login()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

    @browsing
    def test_tooltip(self, browser):
        browser.login()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='tooltip')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

    @browsing
    def test_bumblebee(self, browser):
        browser.login()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(['Edit metadata',
                          'Attach to email',
                          'Download copy',
                          'Open as PDF',
                          'Open detail view'],
                         browser.css('.file-action-buttons a').text)

        self.assertIn("javascript:officeConnectorAttach('",
                      browser.css('a.function-attach')[0].get('href'))

    @browsing
    def test_tabbed(self, browser):
        browser.login()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeConnectorSettings)

        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Send as email',
                          'Export selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)

        transaction.commit()

        browser.open(self.dossier, view='tabbedview_view-documents')

        self.assertEqual([u'More actions \u25bc',
                          'Copy Items',
                          'Export selection',
                          'Attach selection',
                          'Move Items',
                          'Export as Zip'],
                         browser.css('.tabbedview-action-list a').text)

        self.assertIn("javascript:officeConnectorMultiAttach('",
                      browser.css('a.tabbedview-menu-attach_documents')[0]
                      .get('href'))
