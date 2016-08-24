from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import SQLFormSupport
from opengever.base.oguid import Oguid
from opengever.contact import _
from opengever.contact.models.participation_role import ParticipationRole
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ParticipationQuery(BaseQuery):

    def by_oguid(self, oguid):
        return self.filter(Participation.dossier_oguid == oguid)

    def by_oguid_and_contact(self, oguid, contact):
        return self.by_oguid(oguid=oguid).filter(
            Participation.contact == contact)


class Participation(Base, SQLFormSupport):
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

    @property
    def wrapper_id(self):
        return 'participation-{}'.format(self.participation_id)

    def get_url(self, view=u''):
        elements = [self.dossier_oguid.resolve_object().absolute_url(),
                    self.wrapper_id]
        if view:
            elements.append(view)

        return '/'.join(elements)

    def get_title(self):
        return _(u'label_participation_of',
                 default=u'Participation of ${contact_title}',
                 mapping={'contact_title': self.contact.get_title()})

    def resolve_dossier(self):
        return self.dossier_oguid.resolve_object()

    def add_roles(self, role_names):
        for name in role_names:
            role = ParticipationRole(participation=self, role=name)
            create_session().add(role)

    def update_roles(self, role_names):
        """Update the ParticipationRoles of the Participation:
         - Removes existing roles wich are not part of the given `role_names`
         - Keep existing roles wich are part of the given `role_names`
         - Add new roles from `role_names`
        """

        session = create_session()
        new_roles = []

        for existing_role in self.roles:
            if existing_role.role not in role_names:
                session.delete(existing_role)
            else:
                new_roles.append(existing_role)
                role_names.remove(existing_role.role)

        for name in role_names:
            role = ParticipationRole(role=name)
            create_session().add(role)
            new_roles.append(role)

        self.roles = new_roles

    def delete(self):
        session = create_session()
        for role in self.roles:
            session.delete(role)

        session.delete(self)


Participation.query_cls = ParticipationQuery
