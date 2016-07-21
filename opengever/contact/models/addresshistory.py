from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import ZIP_CODE_LENGTH
from opengever.contact.models.history import HistoryMixin
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class AddressHistory(HistoryMixin, Base):

    __tablename__ = 'addresseshistory'

    address_history_id = Column('id', Integer,
                                Sequence('addresseshistory_id_seq'),
                                primary_key=True)
    contact = relationship("Contact", back_populates="address_history")
    label = Column(String(CONTENT_TITLE_LENGTH))
    street = Column(String(CONTENT_TITLE_LENGTH))
    zip_code = Column(String(ZIP_CODE_LENGTH))
    city = Column(String(CONTENT_TITLE_LENGTH))
