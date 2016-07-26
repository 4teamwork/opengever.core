from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import create_session
from opengever.base.model import ZIP_CODE_LENGTH
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

    def serialize(self):
        return {
            'id': self.address_id,
            'contact_id': self.contact_id,
            'label': self.label,
            'street': self.street,
            'zip_code': self.zip_code,
            'city': self.city,
            'delete_url': self.get_delete_url(),
            'update_url': self.get_update_url(),
        }

    def delete(self):
        session = create_session()
        session.delete(self)

    def get_delete_url(self):
        return self.contact.get_url(
            'addresses/{}/delete'.format(self.address_id))

    def get_update_url(self):
        return self.contact.get_url(
            'addresses/{}/update'.format(self.address_id))
