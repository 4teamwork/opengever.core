from opengever.base.model import UTCDateTime
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
            Column('text_en', String, nullable=True),
            Column('text_de', String, nullable=True),
            Column('text_fr', String, nullable=True),
            Column('start', UTCDateTime(timezone=True), nullable=False),
            Column('end', UTCDateTime(timezone=True), nullable=False),
            Column('type', String, nullable=False),

        )
        self.ensure_sequence_exists('system_message_id_seq')
