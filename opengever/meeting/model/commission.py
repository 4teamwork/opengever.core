from opengever.core.model import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class Commission(Base):

    __tablename__ = 'commissions'

    commission_id = Column("id", Integer, Sequence("commission_id_seq"),
                           primary_key=True)
    title = Column(String(256))

    def __repr__(self):
        return '<Commission "{}">'.format(self.title)
