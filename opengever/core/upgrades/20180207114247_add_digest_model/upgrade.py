from opengever.base.model import UTCDateTime
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class AddDigestModel(SchemaMigration):
    """Add Digest model.
    """

    def migrate(self):
        self.op.create_table(
            'digests',
            Column("id", Integer, Sequence('digest_id_seq'), primary_key=True),
            Column("userid", String(255), nullable=False),
            Column("last_dispatch", UTCDateTime(timezone=True))
        )

        self.ensure_sequence_exists('digest_id_seq')
