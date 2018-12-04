from opengever.base.model import Base
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.oguid import Oguid
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Excerpt(Base):
    """Relation to an excerpt for ad-hoc agenda items."""

    __tablename__ = 'excerpts'

    excerpt_id = Column("id", Integer, Sequence("excerpts_id_seq"),
                        primary_key=True)
    agenda_item_id = Column(Integer, ForeignKey('agendaitems.id'))
    agenda_item = relationship("AgendaItem", uselist=False,
                               backref=backref('excerpts'))

    excerpt_admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    excerpt_int_id = Column(Integer, nullable=False)
    excerpt_oguid = composite(
        Oguid, excerpt_admin_unit_id, excerpt_int_id)

    def resolve_document(self):
        return self.excerpt_oguid.resolve_object()
