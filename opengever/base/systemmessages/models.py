from opengever.base.model import Base
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import UTCDateTime
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy.orm import relationship


tables = [
    'system-messages',
]


class SystemMessages(Base):

    __tablename__ = 'system_messages'

    id = Column(Integer, Sequence('system_message_id_seq'), primary_key=True)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=True)
    admin_unit = relationship('AdminUnit', foreign_keys=[admin_unit_id])
    text_en = Column(String, nullable=True)
    text_de = Column(String, nullable=True)
    text_fr = Column(String, nullable=True)
    start = Column(UTCDateTime(timezone=True), nullable=False)
    end = Column(UTCDateTime(timezone=True), nullable=False)
    type = Column(String, nullable=False)
