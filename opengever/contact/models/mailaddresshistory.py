from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.history import HistoryMixin
from opengever.ogds.models import EMAIL_LENGTH
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class MailAddressHistory(HistoryMixin, Base):

    __tablename__ = 'mail_addresses_history'

    mailaddress_history_id = Column(
        'id', Integer, Sequence('mail_adresses_history_id_seq'),
        primary_key=True)
    contact = relationship("Contact", back_populates="mail_address_history")
    label = Column(String(CONTENT_TITLE_LENGTH))
    address = Column(String(EMAIL_LENGTH))
