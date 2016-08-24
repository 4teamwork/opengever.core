from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.archive import ArchiveMixin
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ArchivedPhoneNumber(ArchiveMixin, Base):

    __tablename__ = 'archived_phonenumbers'

    archived_phonenumber_id = Column(
        'id', Integer, Sequence('archived_phonenumber_id_seq'),
        primary_key=True)
    contact = relationship("Contact", back_populates="archived_phonenumbers")

    label = Column(String(CONTENT_TITLE_LENGTH))
    phone_number = Column(String(CONTENT_TITLE_LENGTH))
