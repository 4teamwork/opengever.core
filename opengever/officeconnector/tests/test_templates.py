from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from plone import api

import transaction


class TestOfficeConnectorTemplates(FunctionalTestCase):
    """Test templates to ensure OC can function."""

    def setUp(self):
        super(TestOfficeConnectorTemplates, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier').within(self.repo))
        self.document = create(Builder('document')
                               .titled('testdocu')
                               .within(self.dossier)
                               .attach_file_containing(
                                   bumblebee_asset('example.docx')
                                   .bytes(),
                                   u'example.docx',
                                   )
                               )

    @browsing
    def test_overview_template_without_officeconnector(self, browser):
        browser.login().open(self.document, view='tabbedview_view-overview')

        self.assertFalse(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertEqual(0, len(browser.css('a.function-attach')))

    @browsing
    def test_tooltip_template_without_officeconnector(self, browser):
        browser.login().open(self.document, view='tooltip')

        self.assertFalse(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertEqual(0, len(browser.css('a.function-attach')))

    @browsing
    def test_overview_template_with_officeconnector_attach(self, browser):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-overview')

        self.assertFalse(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertEqual(1, len(browser.css('a.function-attach')))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-attach').first.get('href'))

    @browsing
    def test_overview_template_with_officeconnector_checkout(self, browser):
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-overview')

        self.assertEqual(0, len(browser.css('a.function-attach')))

        self.assertTrue(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-edit').first.get('href'))

    @browsing
    def test_overview_template_with_officeconnector_attach_and_checkout(self, browser): # noqa
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-overview')

        self.assertEqual(1, len(browser.css('a.function-attach')))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-attach').first.get('href'))

        self.assertTrue(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-edit').first.get('href'))

    @browsing
    def test_tooltip_template_with_officeconnector_attach(self, browser):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='tooltip')

        self.assertFalse(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertEqual(1, len(browser.css('a.function-edit')))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-attach').first.get('href'))

    @browsing
    def test_tooltip_template_with_officeconnector_checkout(self, browser):
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='tooltip')

        self.assertEqual(0, len(browser.css('a.function-attach')))

        self.assertTrue(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-edit').first.get('href'))

    @browsing
    def test_tooltip_template_with_officeconnector_attach_and_checkout(self, browser): #noqa
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='tooltip')

        self.assertEqual(1, len(browser.css('a.function-attach')))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-attach').first.get('href'))

        self.assertTrue(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-edit').first.get('href'))


class TestOfficeConnectorBumblebeeTemplates(FunctionalTestCase):
    """Test Bumblebee templates to ensure OC can function."""

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOfficeConnectorBumblebeeTemplates, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier').within(self.repo))
        self.document = create(Builder('document')
                               .titled('testdocu')
                               .within(self.dossier)
                               .attach_file_containing(
                                   bumblebee_asset('example.docx')
                                   .bytes(),
                                   u'example.docx',
                                   )
                               )

    @browsing
    def test_bumblebeeoverlay_template_without_officeconnector(self, browser):
        browser.login().open(self.document, view='bumblebee-overlay-listing')

        self.assertFalse(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertEqual(0, len(browser.css('a.function-attach')))

    @browsing
    def test_bumblebeeoverlay_template_with_officeconnector_attach(self, browser): #noqa
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='bumblebee-overlay-listing')

        self.assertFalse(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertEqual(1, len(browser.css('a.function-edit')))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-attach').first.get('href'))

    @browsing
    def test_bumblebeeoverlay_template_with_officeconnector_checkout(self, browser): #noqa
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(0, len(browser.css('a.function-attach')))

        self.assertTrue(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-edit').first.get('href'))

    @browsing
    def test_bumblebeeoverlay_template_with_officeconnector_attach_and_checkout(self, browser): #noqa
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        browser.login().open(self.document, view='bumblebee-overlay-listing')

        self.assertEqual(1, len(browser.css('a.function-attach')))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-attach').first.get('href'))

        self.assertTrue(
            'javascript:officeConnectorCheckout('
            in browser.css('a.function-edit').first.get('href'))

        self.assertTrue(
            self.document.absolute_url()
            in browser.css('a.function-edit').first.get('href'))
