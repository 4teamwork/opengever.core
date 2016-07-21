from opengever.contact.models import Address
from opengever.contact.models import ArchivedAddress
from opengever.contact.models import ArchivedMailAddress
from opengever.contact.models import ArchivedPhoneNumber
from opengever.contact.models import ArchivedURL
from opengever.contact.models import Contact
from opengever.contact.models import ContactHistory
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import OrganizationHistory
from opengever.contact.models import Person
from opengever.contact.models import PersonHistory
from opengever.contact.models import PhoneNumber
from opengever.contact.models import URL
from sqlalchemy import inspect
from unittest2 import TestCase


class TestArchiveTables(TestCase):
    """Test that archive tables contain all required columns.

    When this test fails it most likely means that you have added columns to
    a table but forgot to update the corresponding archive table.

    """
    additional_archive_columns = ['contact_id', 'actor_id', 'created']

    def get_column_names(self, entity, ignore):
        return [column.name for column in inspect(entity).columns
                if column.name not in ignore]

    def assert_correct_archiv_entity(self, entity, archive_entity, ignore=None):
        ignore = ignore or []
        entity_columns = self.get_column_names(entity, ignore)
        archive_entity_columns = self.get_column_names(archive_entity, ignore)

        self.assertEqual(
            set(entity_columns + self.additional_archive_columns),
            set(archive_entity_columns))

    def test_address_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(Address, ArchivedAddress)

    def test_contact_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(
            Contact, ContactHistory,
            ignore=['contact_type', 'contact_history_type'])

    def test_mail_address_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(MailAddress, ArchivedMailAddress)

    def test_phonenumber_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(PhoneNumber, ArchivedPhoneNumber)

    def test_url_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(URL, ArchivedURL)

    def test_person_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(
            Person, PersonHistory,
            ignore=['contact_type', 'contact_history_type'])

    def test_organization_archive_contains_all_columns(self):
        self.assert_correct_archiv_entity(
            Organization, OrganizationHistory,
            ignore=['contact_type', 'contact_history_type'])
