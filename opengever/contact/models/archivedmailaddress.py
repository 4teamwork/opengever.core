from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import EMAIL_LENGTH
from opengever.contact.models.archive import ArchiveMixin
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ArchivedMailAddress(ArchiveMixin, Base):

    __tablename__ = 'archived_mail_addresses'

    archived_mail_address_id = Column(
        'id', Integer, Sequence('archived_mail_address_id_seq'),
        primary_key=True)
    contact = relationship("Contact", back_populates="archived_mail_addresses")
    label = Column(String(CONTENT_TITLE_LENGTH))
    address = Column(String(EMAIL_LENGTH))
