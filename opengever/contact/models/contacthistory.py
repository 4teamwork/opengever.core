from opengever.base.model import Base
from opengever.contact.models.history import HistoryMixin
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ContactHistory(HistoryMixin, Base):

    __tablename__ = 'contactshistory'

    contact_history_id = Column('id', Integer,
                                Sequence('contactshistory_id_seq'),
                                primary_key=True)
    contact = relationship("Contact", back_populates="history")
    description = Column(UnicodeCoercingText)

    contact_history_type = Column(String(20), nullable=False)
    __mapper_args__ = {'polymorphic_on': contact_history_type,
                       'with_polymorphic': '*'}
