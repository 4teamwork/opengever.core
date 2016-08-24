from opengever.base.model import Base
from opengever.contact.models.archive import ArchiveMixin
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ArchivedContact(ArchiveMixin, Base):

    __tablename__ = 'archived_contacts'

    archived_contact_id = Column('id', Integer,
                                 Sequence('archived_contact_id_seq'),
                                 primary_key=True)
    contact = relationship("Contact", back_populates="archived_contacts")
    description = Column(UnicodeCoercingText)

    archived_contact_type = Column(String(30), nullable=False)
    __mapper_args__ = {'polymorphic_on': archived_contact_type,
                       'with_polymorphic': '*'}
