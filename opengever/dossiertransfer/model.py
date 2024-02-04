from datetime import timedelta
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.base.types import JSONList
from opengever.base.types import UnicodeCoercingText
from opengever.dossiertransfer.token import TokenManager
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
import hashlib
import json


tables = [
    'dossier_transfers',
]

TRANSFER_STATE_PENDING = 'pending'
TRANSFER_STATE_COMPLETED = 'completed'


def in_30d():
    return utcnow_tz_aware() + timedelta(days=30)


class DossierTransfer(Base):

    __tablename__ = 'dossier_transfers'

    id = Column('id', Integer, Sequence('dossier_transfer_id_seq'), primary_key=True)
    title = Column(UnicodeCoercingText(), nullable=False)
    message = Column(UnicodeCoercingText(), nullable=True, default=u'')
    created = Column(UTCDateTime(timezone=True), nullable=False, default=utcnow_tz_aware)
    expires = Column(UTCDateTime(timezone=True), nullable=False, default=in_30d)
    state = Column(String(32), nullable=False)

    source_id = Column(String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=False)
    source = relationship("AdminUnit", foreign_keys=[source_id])

    target_id = Column(String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=False)
    target = relationship("AdminUnit", foreign_keys=[target_id])

    source_user_id = Column(String(USER_ID_LENGTH), ForeignKey('users.userid'), nullable=True)
    source_user = relationship("User")

    root = Column(String(32), nullable=False)
    documents = Column(JSONList(), nullable=True)
    participations = Column(JSONList(), nullable=True)

    all_documents = Column(Boolean(), nullable=False)
    all_participations = Column(Boolean(), nullable=False)

    token = Column(String(), nullable=True)

    def __repr__(self):
        return '<DossierTransfer {} ({} -> {})>'.format(
            self.id, self.source_id, self.target_id)

    def issue_token(self):
        return TokenManager().issue_token(self)

    def validate_token(self, token):
        TokenManager().validate_token(self, token)

    def attributes_hash(self):
        """Create a hash over all attributes that are relevant for security.

        We could put those in the JWT and have the JWT's signature cover them,
        but the 'documents' and 'participations' lists may grow large, and
        would make the size of the JWT be dynamic.
        """
        documents = self.documents if self.documents else []
        participations = self.participations if self.participations else []

        data = json.dumps({
            'state': self.state,
            'target_id': self.target_id,
            'source_user_id': self.source_user_id,
            'root': self.root,
            'documents': sorted(documents),
            'participations': sorted(participations),
            'all_documents': self.all_documents,
            'all_participations': self.all_participations,
        }, sort_keys=True)
        return hashlib.sha256(data).hexdigest()
