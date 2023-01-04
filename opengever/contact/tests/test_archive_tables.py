from opengever.contact.models import Address
from opengever.contact.models import ArchivedAddress
from opengever.contact.models import ArchivedContact
from opengever.contact.models import ArchivedMailAddress
from opengever.contact.models import ArchivedURL
from opengever.contact.models import Contact
from opengever.contact.models import MailAddress
from opengever.contact.models import URL
from sqlalchemy import inspect
from unittest import TestCase


class TestArchiveTables(TestCase):
    """Test that archive tables contain all required columns.

    When this test fails it most likely means that you have added columns to
    a table but forgot to update the corresponding archive table.

    """
    additional_archive_columns = ['contact_id', 'actor_id', 'created']

    def get_column_names(self, entity, ignore):
        return [column.name for column in inspect(entity).columns
                if column.name not in ignore]

    def assert_correct_archive_entity(self, entity, archive_entity, ignore=None):
        ignore = ignore or []
        entity_columns = self.get_column_names(entity, ignore)
        archive_entity_columns = self.get_column_names(archive_entity, ignore)

        self.assertEqual(
            set(entity_columns + self.additional_archive_columns),
            set(archive_entity_columns))

    def test_address_archive_contains_all_columns(self):
        self.assert_correct_archive_entity(Address, ArchivedAddress)

    def test_contact_archive_contains_all_columns(self):
        self.assert_correct_archive_entity(
            Contact, ArchivedContact,
            ignore=['contact_type', 'archived_contact_type', 'former_contact_id'])

    def test_mail_address_archive_contains_all_columns(self):
        self.assert_correct_archive_entity(MailAddress, ArchivedMailAddress)

    def test_url_archive_contains_all_columns(self):
        self.assert_correct_archive_entity(URL, ArchivedURL)
