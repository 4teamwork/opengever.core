from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import ZIP_CODE_LENGTH
from opengever.contact.docprops import AddressDocPropertyProvider
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Address(Base):
    __tablename__ = 'addresses'

    address_id = Column('id', Integer, Sequence('adresses_id_seq'),
                        primary_key=True)
    contact_id = Column('contact_id', Integer, ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="addresses")
    label = Column(String(CONTENT_TITLE_LENGTH))
    street = Column(String(CONTENT_TITLE_LENGTH))
    zip_code = Column(String(ZIP_CODE_LENGTH))
    city = Column(String(CONTENT_TITLE_LENGTH))
    country = Column(String(CONTENT_TITLE_LENGTH))

    def get_lines(self):
        """Return a list of all address-lines that are not empty."""

        return filter(None, [
            self.contact.get_title(),
            self.street,
            u" ".join(filter(None, [self.zip_code, self.city])),
            self.country
        ])

    def get_doc_property_provider(self):
        return AddressDocPropertyProvider(self)
