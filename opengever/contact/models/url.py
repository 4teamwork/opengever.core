from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.docprops import URLDocPropertyProvider
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
    url = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    def get_doc_property_provider(self):
        return URLDocPropertyProvider(self)
