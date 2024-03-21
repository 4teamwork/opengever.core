from opengever.base.model import UTCDateTime
from opengever.base.types import UnicodeCoercingText
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


UNIT_ID_LENGTH = 30


class AddSystemMessagesSQLTable(SchemaMigration):
    """Add system_messages SQL table.
    """

    def migrate(self):
        self.op.create_table(
            'system_messages',
            Column('id', Integer, Sequence('system_message_id_seq'), primary_key=True),
            Column('admin_unit_id', String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=True),
            Column('text_en', UnicodeCoercingText, nullable=True),
            Column('text_de', UnicodeCoercingText, nullable=True),
            Column('text_fr', UnicodeCoercingText, nullable=True),
            Column('start_ts', UTCDateTime(timezone=True), nullable=False),
            Column('end_ts', UTCDateTime(timezone=True), nullable=False),
            Column('type', String(30), nullable=False),

        )
        self.ensure_sequence_exists('system_message_id_seq')
