from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.ogds.models import EMAIL_LENGTH
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class MailAddress(Base):
    __tablename__ = 'mail_addresses'

    mailaddress_id = Column('id', Integer, Sequence('mail_adresses_id_seq'),
                            primary_key=True)
    contact_id = Column('contact_id', Integer, ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="mail_addresses")
    label = Column(String(CONTENT_TITLE_LENGTH))
    address = Column(String(EMAIL_LENGTH))
