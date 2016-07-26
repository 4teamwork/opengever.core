from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import create_session
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class URL(Base):
    __tablename__ = 'urls'

    url_id = Column('id', Integer, Sequence('urls_id_seq'),
                    primary_key=True)
    contact_id = Column('contact_id', Integer, ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="urls")
    label = Column(String(CONTENT_TITLE_LENGTH))
    url = Column(String(CONTENT_TITLE_LENGTH))

    def serialize(self):
        return {
            'id': self.url_id,
            'contact_id': self.contact_id,
            'label': self.label,
            'url': self.url,
            'delete_url': self.get_delete_url(),
            'update_url': self.get_update_url(),
        }

    def delete(self):
        session = create_session()
        session.delete(self)

    def get_delete_url(self):
        return self.contact.get_url('urls/{}/delete'.format(self.url_id))

    def get_update_url(self):
        return self.contact.get_url('urls/{}/update'.format(self.url_id))
