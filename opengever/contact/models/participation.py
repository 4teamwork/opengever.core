from opengever.base.model import Base
from opengever.base.oguid import Oguid
from opengever.ogds.models import UNIT_ID_LENGTH
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Participation(Base):
    """Lets contacts participate in dossiers with specified roles.
    """

    __tablename__ = 'participations'

    participation_id = Column('id', Integer, Sequence('participations_id_seq'),
                              primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    contact = relationship('Contact', back_populates='participations')
    dossier_admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    dossier_int_id = Column(Integer, nullable=False)
    dossier_oguid = composite(Oguid, dossier_admin_unit_id, dossier_int_id)
    roles = relationship('ParticipationRole', back_populates='participation')

    def resolve_dossier(self):
        return self.dossier_oguid.resolve_object()
