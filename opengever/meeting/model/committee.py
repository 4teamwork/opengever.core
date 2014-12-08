from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class Committee(Base):

    __tablename__ = 'committees'

    committee_id = Column("id", Integer, Sequence("committee_id_seq"),
                           primary_key=True)
    title = Column(String(256))

    def __repr__(self):
        return '<Committee "{}">'.format(self.title)
