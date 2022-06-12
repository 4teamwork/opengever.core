from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


CONTENT_TITLE_LENGTH = 255
EMPTY_URL_PLACEHOLDER = u'<No URL>'


class MakeURLRequired(SchemaMigration):
    """Make URL required.
    """

    def migrate(self):
        self.insert_placeholders()
        self.make_column_required()

    def insert_placeholders(self):
        """Fill empty URLs with a placeholder.
        """
        url_table = table('urls',
                          column("id"),
                          column("url"))

        self.execute(url_table.update()
                     .values(url=EMPTY_URL_PLACEHOLDER)
                     .where(url_table.columns.url.is_(None)))

    def make_column_required(self):
        self.op.alter_column(
            'urls', 'url',
            existing_type=String(CONTENT_TITLE_LENGTH), nullable=False)
