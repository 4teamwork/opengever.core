from opengever.base.model import Base
from opengever.base.model import SQLFormSupport
from opengever.contact.models.participation import ContactParticipation
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Contact(Base, SQLFormSupport):
    """Base class for both type of contacts organizations and persons.
    """

    participation_class = ContactParticipation

    __tablename__ = 'contacts'

    contact_id = Column('id', Integer, Sequence('contacts_id_seq'),
                        primary_key=True)
    contact_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    description = Column(UnicodeCoercingText)

    addresses = relationship("Address", back_populates="contact")
    mail_addresses = relationship(
        "MailAddress",
        back_populates="contact",
        order_by='MailAddress.mailaddress_id')

    phonenumbers = relationship("PhoneNumber", back_populates="contact")
    urls = relationship("URL", back_populates="contact")
    participations = relationship("ContactParticipation",
                                  back_populates="contact")

    archived_contacts = relationship("ArchivedContact", back_populates="contact")
    archived_addresses = relationship("ArchivedAddress", back_populates="contact")
    archived_mail_addresses = relationship("ArchivedMailAddress", back_populates="contact")
    archived_phonenumbers = relationship("ArchivedPhoneNumber", back_populates="contact")
    archived_urls = relationship("ArchivedURL", back_populates="contact")

    __mapper_args__ = {'polymorphic_on': contact_type,
                       'with_polymorphic': '*'}

    @property
    def id(self):
        return self.contact_id
