from opengever.base.model import Base
from sqlalchemy import String
from opengever.base.model import UTCDateTime
from sqlalchemy import Integer
from sqlalchemy.schema import Sequence
from opengever.ogds.models import USER_ID_LENGTH
from sqlalchemy import Column


class Digest(Base):

    __tablename__ = 'digests'

    digest_id = Column('id', Integer,
                       Sequence('digest_id_seq'), primary_key=True)
    userid = Column(String(USER_ID_LENGTH), nullable=False)
    last_dispatch = Column(UTCDateTime(timezone=True))
