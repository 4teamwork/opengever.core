from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import create_session
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
    phone_number = Column(String(CONTENT_TITLE_LENGTH))

    def serialize(self):
        return {
            'id': self.phone_number_id,
            'contact_id': self.contact_id,
            'label': self.label,
            'phone_number': self.phone_number,
            'delete_url': self.get_delete_url(),
            'update_url': self.get_update_url(),
        }

    def delete(self):
        session = create_session()
        session.delete(self)

    def get_delete_url(self):
        return self.contact.get_url(
            'phonenumbers/{}/delete'.format(self.phone_number_id))

    def get_update_url(self):
        return self.contact.get_url(
            'phonenumbers/{}/update'.format(self.phone_number_id))
