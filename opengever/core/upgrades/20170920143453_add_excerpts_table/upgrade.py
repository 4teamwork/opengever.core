from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


UNIT_ID_LENGTH = 30


class AddExcerptsTable(SchemaMigration):
    """Add excerpts table.
    """

    def migrate(self):
        self.op.create_table(
            'excerpts',
            Column('id', Integer, Sequence('excerpts_id_seq'),
                   primary_key=True),

            Column('agenda_item_id', Integer, ForeignKey('agendaitems.id')),
            Column('excerpt_admin_unit_id',
                   String(UNIT_ID_LENGTH), nullable=False),
            Column('excerpt_int_id', Integer, nullable=False)
        )
        self.ensure_sequence_exists('excerpts_id_seq')
