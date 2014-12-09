from opengever.base.oguid import Oguid
from opengever.core.model import Base
from opengever.meeting.model.query import CommitteeQuery
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class Committee(Base):

    query_cls = CommitteeQuery

    __tablename__ = 'committees'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    committee_id = Column("id", Integer, Sequence("committee_id_seq"),
                          primary_key=True)

    admin_unit_id = Column(String(30), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    title = Column(String(256))

    def __repr__(self):
        return '<Committee "{}">'.format(self.title)
