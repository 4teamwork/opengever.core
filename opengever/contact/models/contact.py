from opengever.base.model import Base
from opengever.base.model import SQLFormSupport
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Contact(Base, SQLFormSupport):
    """Base class for both type of contacts organizations and persons.
    """

    __tablename__ = 'contacts'

    contact_id = Column('id', Integer, Sequence('contacts_id_seq'),
                        primary_key=True)
    contact_type = Column(String(20), nullable=False)
    description = Column(UnicodeCoercingText)

    addresses = relationship("Address", back_populates="contact")
    mail_addresses = relationship(
        "MailAddress",
        back_populates="contact",
        order_by='MailAddress.mailaddress_id')

    phonenumbers = relationship("PhoneNumber", back_populates="contact")
    urls = relationship("URL", back_populates="contact")
    participations = relationship("Participation", back_populates="contact")

    history = relationship("ContactHistory", back_populates="contact")
    address_history = relationship("AddressHistory", back_populates="contact")
    phonenumber_history = relationship("PhoneNumberHistory", back_populates="contact")

    __mapper_args__ = {'polymorphic_on': contact_type,
                       'with_polymorphic': '*'}
