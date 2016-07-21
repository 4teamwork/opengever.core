from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.archive import ArchiveMixin
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ArchivedURL(ArchiveMixin, Base):

    __tablename__ = 'archived_urls'

    archived_url_id = Column('id', Integer, Sequence('archived_url_id_seq'),
                             primary_key=True)
    contact = relationship("Contact", back_populates="archived_urls")
    label = Column(String(CONTENT_TITLE_LENGTH))
    url = Column(String(CONTENT_TITLE_LENGTH))
