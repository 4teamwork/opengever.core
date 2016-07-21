from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.history import HistoryMixin
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class PhoneNumberHistory(HistoryMixin, Base):

    __tablename__ = 'phonenumbershistory'

    phone_number_history_id = Column(
        'id', Integer, Sequence('phonenumbershistory_id_seq'),
        primary_key=True)
    contact = relationship("Contact", back_populates="phonenumber_history")

    label = Column(String(CONTENT_TITLE_LENGTH))
    phone_number = Column(String(CONTENT_TITLE_LENGTH))
