from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql import select
import logging


log = logging.getLogger('ftw.upgrade')

contacts_table_names = (
    'addresses',
    'archived_addresses',
    'archived_contacts',
    'archived_mail_addresses',
    'archived_organizations',
    'archived_persons',
    'archived_phonenumbers',
    'archived_urls',
    'contacts',
    'mail_addresses',
    'org_roles',
    'organizations',
    'participation_roles',
    'participations',
    'persons',
    'phonenumbers',
    'urls',
)


class NonEmptyContactsTable(Exception):
    """Raised when migration precondition is violated."""


class DropSQLContactsTables(SchemaMigration):
    """Drop SQL contacts tables.

    All SQL contacts data should have been migrated by previous migrations.
    Therefore we can assert that the tables being dropped are empty.
    """

    def migrate(self):
        self.assert_tables_empty()

        # Drop tables in proper order:
        #
        # MetaData.sorted_tables lists tables in dependency order. By
        # iterating over them in reverse order we ensure that our DROP TABLEs
        # won't fail because of FK constraints, and can avoid having to use
        # DROP TABLE ... CASCADE, which would make for a really bad day if
        # it goes wrong in production.

        for tbl in reversed(self.metadata.sorted_tables):
            if tbl.name not in contacts_table_names:
                continue

            log.info('Dropping SQL contacts table {!r}'.format(tbl.name))
            self.op.drop_table(tbl.name)

    def assert_tables_empty(self):
        for tbl in self.metadata.sorted_tables:
            if tbl.name not in contacts_table_names:
                continue

            rowcount = self.execute(select([tbl])).rowcount
            if rowcount > 0:
                raise NonEmptyContactsTable(
                    "Expected empty contact table {!r}, found {} rows".format(
                        tbl.name, rowcount))
