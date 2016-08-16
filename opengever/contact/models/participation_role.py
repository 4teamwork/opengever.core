from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ParticipationRole(Base):
    """Defines a role of a participating contact.
    """

    __tablename__ = 'participation_roles'

    participation_role_id = Column('id', Integer,
                                   Sequence('participation_roles_id_seq'),
                                   primary_key=True)
    participation_id = Column(Integer, ForeignKey('participations.id'),
                              nullable=False)
    participation = relationship('Participation', back_populates='roles')
    role = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    def __repr__(self):
        return u'<ParticipationRole {} >'.format(self.role)
