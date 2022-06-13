from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


CONTENT_TITLE_LENGTH = 255
EMPTY_PHONE_NUMBER_PLACEHOLDER = u'<No phone number>'


class MakePhoneNumberRequired(SchemaMigration):
    """Make phone_number required.
    """

    def migrate(self):
        self.insert_placeholders()
        self.make_column_required()

    def insert_placeholders(self):
        """Fill empty phone_number with a placeholder.
        """
        phonenumbers_table = table('phonenumbers',
                                   column("id"),
                                   column("phone_number"))

        self.execute(phonenumbers_table.update()
                     .values(phone_number=EMPTY_PHONE_NUMBER_PLACEHOLDER)
                     .where(phonenumbers_table.columns.phone_number.is_(None)))

    def make_column_required(self):
        self.op.alter_column(
            'phonenumbers', 'phone_number',
            existing_type=String(CONTENT_TITLE_LENGTH), nullable=False)
