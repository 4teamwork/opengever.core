from opengever.base.model import UTCDateTime
from opengever.base.types import JSONList
from opengever.base.types import UnicodeCoercingText
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


UNIT_ID_LENGTH = 30
USER_ID_LENGTH = 255


class AddDossierTransfersSQLTable(SchemaMigration):
    """Add dossier_transfers SQL table.
    """

    def migrate(self):
        self.op.create_table(
            'dossier_transfers',
            Column('id', Integer, Sequence('dossier_transfer_id_seq'), primary_key=True),
            Column('title', UnicodeCoercingText(), nullable=False),
            Column('message', UnicodeCoercingText(), nullable=True),
            Column('created', UTCDateTime(timezone=True), nullable=False),
            Column('expires', UTCDateTime(timezone=True), nullable=False),
            Column('state', String(32), nullable=False),
            Column('source_id', String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=False),
            Column('target_id', String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=False),
            Column('source_user_id', String(USER_ID_LENGTH), ForeignKey('users.userid'), nullable=True),
            Column('root', String(32), nullable=False),
            Column('documents', JSONList(), nullable=True),
            Column('participations', JSONList(), nullable=True),
            Column('all_documents', Boolean(), nullable=False),
            Column('all_participations', Boolean(), nullable=False),
            Column('token', String(), nullable=True),
        )
