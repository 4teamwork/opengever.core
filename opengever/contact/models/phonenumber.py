from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.docprops import PhoneNumberDocPropertyProvider
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class PhoneNumber(Base):

    __tablename__ = 'phonenumbers'

    phone_number_id = Column('id', Integer, Sequence('phonenumber_id_seq'),
                        primary_key=True)
    contact_id = Column('contact_id', Integer, ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="phonenumbers")

    label = Column(String(CONTENT_TITLE_LENGTH))
    phone_number = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    def get_doc_property_provider(self):
        return PhoneNumberDocPropertyProvider(self)
