from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


CONTENT_TITLE_LENGTH = 255
USER_ID_LENGTH = 255


class AddPhoneNumberHistory(SchemaMigration):
    """Add phonenumber history.
    """

    def migrate(self):
        self.add_phonenumber_history_table()

    def add_phonenumber_history_table(self):
        self.op.create_table(
            'phonenumbershistory',
            Column('id', Integer, Sequence('phonenumbershistory_id_seq'),
                   primary_key=True),
            Column('contact_id', Integer, ForeignKey('contacts.id'),
                   nullable=False),
            Column('actor_id', String(USER_ID_LENGTH), nullable=False),
            Column('created', DateTime(timezone=True)),
            Column('label', String(CONTENT_TITLE_LENGTH)),
            Column('phone_number', String(CONTENT_TITLE_LENGTH)),
        )
