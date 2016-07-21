from opengever.contact.models import Address
from opengever.contact.models import AddressHistory
from opengever.contact.models import Contact
from opengever.contact.models import ContactHistory
from opengever.contact.models import MailAddress
from opengever.contact.models import MailAddressHistory
from opengever.contact.models import Organization
from opengever.contact.models import OrganizationHistory
from opengever.contact.models import Person
from opengever.contact.models import PersonHistory
from opengever.contact.models import PhoneNumber
from opengever.contact.models import PhoneNumberHistory
from sqlalchemy import inspect
from unittest2 import TestCase


class TestHistoryTables(TestCase):
    """Test that history tables contain all required columns.

    When this test fails it most likely means that you have added columns to
    a table but forgot to update the corresponding history table.

    """
    additional_history_columns = ['contact_id', 'actor_id', 'created']

    def get_column_names(self, entity, ignore):
        return [column.name for column in inspect(entity).columns
                if column.name not in ignore]

    def assert_correct_history_entity(self, entity, history_entity, ignore=None):
        ignore = ignore or []
        entity_columns = self.get_column_names(entity, ignore)
        history_entity_columns = self.get_column_names(history_entity, ignore)

        self.assertEqual(
            set(entity_columns + self.additional_history_columns),
            set(history_entity_columns))

    def test_address_history_contains_all_columns(self):
        self.assert_correct_history_entity(Address, AddressHistory)

    def test_contact_history_contains_all_columns(self):
        self.assert_correct_history_entity(
            Contact, ContactHistory,
            ignore=['contact_type', 'contact_history_type'])

    def test_mail_address_history_contains_all_columns(self):
        self.assert_correct_history_entity(MailAddress, MailAddressHistory)

    def test_phonenumber_history_contains_all_columns(self):
        self.assert_correct_history_entity(PhoneNumber, PhoneNumberHistory)

    def test_person_history_contains_all_columns(self):
        self.assert_correct_history_entity(
            Person, PersonHistory,
            ignore=['contact_type', 'contact_history_type'])

    def test_organization_history_contains_all_columns(self):
        self.assert_correct_history_entity(
            Organization, OrganizationHistory,
            ignore=['contact_type', 'contact_history_type'])
