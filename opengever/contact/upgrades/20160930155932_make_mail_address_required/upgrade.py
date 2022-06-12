from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


EMAIL_LENGTH = 255
EMPTY_ADDRESS_PLACEHOLDER = u'<No Address>'


class MakeMailAddressRequired(SchemaMigration):
    """Make mail address required.
    """

    def migrate(self):
        self.insert_placeholders()
        self.make_column_required()

    def insert_placeholders(self):
        """Fill empty MailAddress with a placeholder.
        """
        mailaddress_table = table('mail_addresses',
                                  column("id"),
                                  column("address"))

        self.execute(mailaddress_table.update()
                     .values(address=EMPTY_ADDRESS_PLACEHOLDER)
                     .where(mailaddress_table.columns.address.is_(None)))

    def make_column_required(self):
        self.op.alter_column(
            'mail_addresses', 'address',
            existing_type=String(EMAIL_LENGTH), nullable=False)
