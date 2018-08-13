from ftw.testbrowser import browsing
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import tabbedview
from plone import api


class TestPrivateReferenceNumber(IntegrationTestCase):

    def test_dotted_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            'formatter',
            'dotted',
            interface=IReferenceNumberSettings,
            )

        expected_reference_numbers = {
            'private_dossier': 'P Client1 kathi-barfuss / 1',
            'private_document': 'P Client1 kathi-barfuss / 1',
            }

        found_reference_numbers = {
            name: getattr(self, name).get_reference_number()
            for name in expected_reference_numbers
            }

        self.assertDictEqual(
            expected_reference_numbers,
            found_reference_numbers,
            )

    def test_grouped_by_three_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            'formatter',
            'grouped_by_three',
            interface=IReferenceNumberSettings,
            )

        expected_reference_numbers = {
            'private_dossier': 'P Client1 kathi-barfuss-1',
            'private_document': 'P Client1 kathi-barfuss-1',
            }

        found_reference_numbers = {
            name: getattr(self, name).get_reference_number()
            for name in expected_reference_numbers
            }

        self.assertDictEqual(
            expected_reference_numbers,
            found_reference_numbers,
            )

    def test_no_client_id_dotted_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            'formatter',
            'no_client_id_dotted',
            interface=IReferenceNumberSettings,
            )

        expected_reference_numbers = {
            'private_dossier': 'P kathi-barfuss / 1',
            'private_document': 'P kathi-barfuss / 1',
            }

        found_reference_numbers = {
            name: getattr(self, name).get_reference_number()
            for name in expected_reference_numbers
            }

        self.assertDictEqual(
            expected_reference_numbers,
            found_reference_numbers,
            )

    def test_no_client_id_grouped_by_three_reference_number(self):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            'formatter',
            'no_client_id_grouped_by_three',
            interface=IReferenceNumberSettings,
            )

        expected_reference_numbers = {
            'private_dossier': 'P kathi-barfuss-1',
            'private_document': 'P kathi-barfuss-1',
            }

        found_reference_numbers = {
            name: getattr(self, name).get_reference_number()
            for name in expected_reference_numbers
            }

        self.assertDictEqual(
            expected_reference_numbers,
            found_reference_numbers,
            )

    @browsing
    def test_prefix_visible_on_private_folder(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.private_folder)
        tabbedview.open('Dossiers')

        urlified_user_id = self.regular_user.id.replace('.', '-')

        expected_reference_numbers = [
            'P Client1 kathi-barfuss / 1',
            'P Client1 kathi-barfuss / 2',
            ]

        found_reference_numbers = [
            item
            for item in browser.css('.listing td').text
            if urlified_user_id in item
            ]

        self.assertEqual(
            len(expected_reference_numbers),
            len(found_reference_numbers),
            )

        self.assertEqual(
            sorted(expected_reference_numbers),
            sorted(found_reference_numbers),
            )

    @browsing
    def test_prefix_visible_on_private_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.private_document)

        expected_reference_number = 'P Client1 kathi-barfuss / 1 / 33'
        found_reference_number = browser.css('.referenceNumber .value').text[0]

        self.assertEqual(found_reference_number, expected_reference_number)
