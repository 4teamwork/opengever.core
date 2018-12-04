from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import SQLFormSupport
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.oguid import Oguid
from opengever.contact import _
from opengever.contact.models.org_role import OrgRole
from opengever.contact.models.participation_role import ParticipationRole
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.ogds.base.utils import ogds_service
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class Participation(Base, SQLFormSupport):
    """Base class for participations.
    """
    __tablename__ = 'participations'

    participation_id = Column('id', Integer, Sequence('participations_id_seq'),
                              primary_key=True)

    dossier_admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    dossier_int_id = Column(Integer, nullable=False)
    dossier_oguid = composite(Oguid, dossier_admin_unit_id, dossier_int_id)
    roles = relationship('ParticipationRole', back_populates='participation')

    participation_type = Column(String(30), nullable=False)
    __mapper_args__ = {'polymorphic_on': participation_type}

    @property
    def participant(self):
        raise NotImplementedError()

    @property
    def wrapper_id(self):
        return 'participation-{}'.format(self.participation_id)

    def get_url(self, context, view=u''):
        elements = [self.dossier_oguid.resolve_object().absolute_url(),
                    self.wrapper_id]
        if view:
            elements.append(view)

        return '/'.join(elements)

    def get_title(self):
        return _(u'label_participation_of',
                 default=u'Participation of ${contact_title}',
                 mapping={'contact_title': self.participant.get_title()})

    def resolve_dossier(self):
        return self.dossier_oguid.resolve_object()

    def get_json_representation(self):
        dossier = self.resolve_dossier()
        return {'title': dossier.title,
                'url': dossier.absolute_url(),
                'roles': [{'label': role.get_label()} for role in self.roles]}

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

    def copy(self):
        copied_participation = self.__class__(**self._get_copied_attributes())
        copied_participation.add_roles([role.role for role in self.roles])
        return copied_participation

    def copy_to_dossier(self, dossier):
        copied_participation = self.copy()
        copied_participation.dossier_oguid = Oguid.for_object(
            dossier, register=True)
        return copied_participation

    def _get_copied_attributes(self):
        return dict(
            dossier_oguid=self.dossier_oguid,
            participation_type=self.participation_type
        )


class OgdsUserParticipation(Participation):
    """Let users from ogds participate in dossiers with a specified role.

    XXX currently ogds is abstracted by a service. Thus we must not add direct
    relations. As soon as this goes away we should change this class and
    include a foreign key to the ogds-user.

    """
    __mapper_args__ = {'polymorphic_identity': 'ogds_user_participation'}

    ogds_userid = Column(String(USER_ID_LENGTH))

    @classmethod
    def create(cls, participant, dossier, roles):
        obj = cls(ogds_user=participant,
                  dossier_oguid=Oguid.for_object(dossier))
        obj.add_roles(roles)
        return obj

    @property
    def ogds_user(self):
        return OgdsUserToContactAdapter(ogds_service().find_user(self.ogds_userid))

    @ogds_user.setter
    def ogds_user(self, ogds_user_adapter):
        self.ogds_userid = ogds_user_adapter.id

    @property
    def participant(self):
        return self.ogds_user

    def _get_copied_attributes(self):
        attributes = super(OgdsUserParticipation, self)._get_copied_attributes()
        attributes['ogds_userid'] = self.ogds_userid
        return attributes

OgdsUserToContactAdapter.participation_class = OgdsUserParticipation


class ContactParticipation(Participation):
    """Let Contacts participate in dossiers with specified roles.
    """
    __mapper_args__ = {'polymorphic_identity': 'contact_participation'}

    contact_id = Column(Integer, ForeignKey('contacts.id'))
    contact = relationship('Contact', back_populates='participations')

    @classmethod
    def create(cls, participant, dossier, roles):
        obj = cls(contact=participant,
                  dossier_oguid=Oguid.for_object(dossier))
        obj.add_roles(roles)
        return obj

    @property
    def participant(self):
        return self.contact

    def _get_copied_attributes(self):
        attributes = super(ContactParticipation, self)._get_copied_attributes()
        attributes['contact'] = self.contact
        return attributes


class OrgRoleParticipation(Participation):
    """Let OrgRoles participate in dossiers with specified roles.
    """
    __mapper_args__ = {'polymorphic_identity': 'org_role_participation'}

    org_role_id = Column(Integer, ForeignKey('org_roles.id'))
    org_role = relationship('OrgRole', back_populates='participations')

    @classmethod
    def create(cls, participant, dossier, roles):
        obj = cls(org_role=participant,
                  dossier_oguid=Oguid.for_object(dossier))
        obj.add_roles(roles)
        return obj

    @property
    def participant(self):
        return self.org_role

    def _get_copied_attributes(self):
        attributes = super(OrgRoleParticipation, self)._get_copied_attributes()
        attributes['org_role'] = self.org_role
        return attributes

OrgRole.participation_class = OrgRoleParticipation
