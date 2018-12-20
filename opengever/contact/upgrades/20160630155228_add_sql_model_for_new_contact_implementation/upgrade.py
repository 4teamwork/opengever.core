from opengever.core.upgrade import SchemaMigration
from opengever.base.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


CONTENT_TITLE_LENGTH = 255
EMAIL_LENGTH = 255
FIRSTNAME_LENGTH = 255
LASTNAME_LENGTH = 255
ZIP_CODE_LENGTH = 16


class AddSQLModelForNewContactImplementation(SchemaMigration):
    """Add SQL Model for new contact implementation.
    """

    def migrate(self):
        """If it is installed on an new plone-site `opengever.base.hooks` takes
        care of that.
        """
        self.add_contact_table()
        self.add_persons_table()
        self.add_organization_table()
        self.add_org_role_table()
        self.add_addresses_table()
        self.add_phonenumbers_table()
        self.add_mail_addresses_table()
        self.add_urls_table()

    def add_contact_table(self):
        self.op.create_table(
            'contacts',
            Column('id', Integer, Sequence('contacts_id_seq'),
                   primary_key=True),
            Column('contact_type', String(20), nullable=False),
            Column('description', UnicodeCoercingText)
        )

    def add_persons_table(self):
        self.op.create_table(
            'persons',
            Column('id', Integer,
                   ForeignKey('contacts.id'), primary_key=True),
            Column('salutation', String(CONTENT_TITLE_LENGTH)),
            Column('academic_title', String(CONTENT_TITLE_LENGTH)),
            Column('firstname', String(FIRSTNAME_LENGTH), nullable=False),
            Column('lastname', String(LASTNAME_LENGTH), nullable=False),
            Column('description', UnicodeCoercingText)
        )

    def add_organization_table(self):
        self.op.create_table(
            'organizations',
            Column('id', Integer, ForeignKey('contacts.id'), primary_key=True),
            Column('contact_type', String(20), nullable=False),
            Column('name', String(CONTENT_TITLE_LENGTH), nullable=False),
            Column('description', UnicodeCoercingText)
        )

    def add_org_role_table(self):
        self.op.create_table(
            'org_roles',
            Column("id", Integer, Sequence("org_roles_id_seq"),
                   primary_key=True),
            Column('person_id', Integer, ForeignKey('persons.id')),
            Column('organization_id', Integer, ForeignKey('organizations.id')),
            Column('function', String(CONTENT_TITLE_LENGTH)),
            Column('description', UnicodeCoercingText)
        )

    def add_addresses_table(self):
        self.op.create_table(
            'addresses',
            Column('id', Integer, Sequence('adresses_id_seq'),
                   primary_key=True),
            Column('contact_id', Integer, ForeignKey('contacts.id')),
            Column('label', String(CONTENT_TITLE_LENGTH)),
            Column('street', String(CONTENT_TITLE_LENGTH)),
            Column('zip_code', String(ZIP_CODE_LENGTH)),
            Column('city', String(CONTENT_TITLE_LENGTH))
        )

    def add_phonenumbers_table(self):
        self.op.create_table(
            'phonenumbers',
            Column('id', Integer, Sequence('phonenumber_id_seq'),
                   primary_key=True),
            Column('contact_id', Integer, ForeignKey('contacts.id')),
            Column('label', String(CONTENT_TITLE_LENGTH)),
            Column('phone_number', String(CONTENT_TITLE_LENGTH))
        )

    def add_mail_addresses_table(self):
        self.op.create_table(
            'mail_addresses',
            Column('id', Integer, Sequence('mail_adresses_id_seq'),
                   primary_key=True),
            Column('contact_id', Integer, ForeignKey('contacts.id')),
            Column('label', String(CONTENT_TITLE_LENGTH)),
            Column('address', String(EMAIL_LENGTH))
        )

    def add_urls_table(self):
        self.op.create_table(
            'urls',
            Column('id', Integer, Sequence('urls_id_seq'), primary_key=True),
            Column('contact_id', Integer, ForeignKey('contacts.id')),
            Column('label', String(CONTENT_TITLE_LENGTH)),
            Column('url', String(CONTENT_TITLE_LENGTH)))
