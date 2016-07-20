from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.schema import Sequence


CONTENT_TITLE_LENGTH = 255
USER_ID_LENGTH = 255
FIRSTNAME_LENGTH = 255
LASTNAME_LENGTH = 255


class AddContactHistory(SchemaMigration):
    """Add contact history.
    """

    def migrate(self):
        self.add_contacts_history_table()
        self.add_organization_history_table()
        self.add_person_history_table()

    def add_contacts_history_table(self):
        self.op.create_table(
            'contactshistory',
            Column('id', Integer, Sequence('contactshistory_id_seq'),
                   primary_key=True),
            Column('contact_id', Integer, ForeignKey('contacts.id'),
                   nullable=False),
            Column('actor_id', String(USER_ID_LENGTH), nullable=False),
            Column('created', DateTime(timezone=True)),
            Column('description', Text),
            Column('contact_history_type', String(20), nullable=False),
        )

    def add_organization_history_table(self):
        self.op.create_table(
            'organizationshistory',
            Column('id', Integer,
                   ForeignKey('contactshistory.id'), primary_key=True),
            Column('name', String(CONTENT_TITLE_LENGTH), nullable=False),
        )

    def add_person_history_table(self):
        self.op.create_table(
            'personshistory',
            Column('id', Integer,
                   ForeignKey('contactshistory.id'), primary_key=True),
            Column('salutation', String(CONTENT_TITLE_LENGTH)),
            Column('academic_title', String(CONTENT_TITLE_LENGTH)),
            Column('firstname', String(FIRSTNAME_LENGTH), nullable=False),
            Column('lastname', String(LASTNAME_LENGTH), nullable=False)
        )
