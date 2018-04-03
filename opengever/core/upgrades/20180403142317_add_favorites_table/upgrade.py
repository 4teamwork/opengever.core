from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import UTCDateTime
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


CONTENT_TITLE_LENGTH = 255
ID_LENGTH = 100
PORTAL_TYPE_LENGTH = 100
UID_LENGTH = 32
UNIT_ID_LENGTH = 30
USER_ID_LENGTH = 255


class AddFavoritesTable(SchemaMigration):
    """Add favorites table.
    """

    def migrate(self):
        self.op.create_table(
            'favorites',
            Column('id', Integer, Sequence("favorites_id_seq"),
                   primary_key=True),
            Column('admin_unit_id', String(UNIT_ID_LENGTH),
                   index=True, nullable=False),
            Column('int_id', Integer, index=True, nullable=False),
            Column('userid', String(USER_ID_LENGTH), index=True),
            Column('position', Integer, index=True),
            Column('title', String(CONTENT_TITLE_LENGTH), nullable=False),
            Column('is_title_personalized', Boolean,
                   default=False, nullable=False),
            Column('portal_type', String(PORTAL_TYPE_LENGTH)),
            Column('icon_class', String(ID_LENGTH)),
            Column('plone_uid', String(UID_LENGTH)),
            Column('created', UTCDateTime(timezone=True), default=utcnow_tz_aware),
            Column('modified', UTCDateTime(timezone=True),
                   default=utcnow_tz_aware, onupdate=utcnow_tz_aware))

        self.ensure_sequence_exists('favorites_id_seq')
