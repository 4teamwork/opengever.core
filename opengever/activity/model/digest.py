from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class Digest(Base):

    __tablename__ = 'digests'

    digest_id = Column('id', Integer,
                       Sequence('digest_id_seq'), primary_key=True)
    userid = Column(String(USER_ID_LENGTH), nullable=False)
    last_dispatch = Column(UTCDateTime(timezone=True))
