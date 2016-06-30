from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class OrgRole(Base):

    __tablename__ = 'org_roles'

    org_role_id = Column("id", Integer,
                         Sequence("org_roles_id_seq"),
                         primary_key=True)

    person_id = Column(Integer, ForeignKey('persons.id'))
    organisation_id = Column(Integer, ForeignKey('organisations.id'))

    organisation = relationship("Organisation", back_populates="persons")
    person = relationship("Person", back_populates="organisations")

    function = Column(String(CONTENT_TITLE_LENGTH))
    description = Column(UnicodeCoercingText)
