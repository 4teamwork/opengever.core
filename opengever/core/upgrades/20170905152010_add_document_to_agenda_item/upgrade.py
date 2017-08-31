from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


UNIT_ID_LENGTH = 30


class AddDocumentToAgendaItem(SchemaMigration):
    """Add document to agenda-item.
    """

    def migrate(self):
        self.op.add_column(
            'agendaitems',
            Column('ad_hoc_document_int_id', Integer))
        self.op.add_column(
            'agendaitems',
            Column('ad_hoc_document_admin_unit_id', String(UNIT_ID_LENGTH)))
