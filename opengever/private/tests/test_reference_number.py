from opengever.base.interfaces import IReferenceNumberSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestPrivateReferenceNumber(IntegrationTestCase):

    def test_dotted_reference_number(self):
        self.login(self.administrator)

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
        self.login(self.administrator)

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
        self.login(self.administrator)

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
        self.login(self.administrator)

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
