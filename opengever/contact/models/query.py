from opengever.base.oguid import Oguid
from opengever.contact.models import Contact
from opengever.contact.models import ContactParticipation
from opengever.contact.models import OgdsUserParticipation
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import OrgRoleParticipation
from opengever.contact.models import Participation
from opengever.contact.models import Person
from opengever.base.query import BaseQuery
from opengever.base.query import extend_query_with_textfilter
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager


class ContactQuery(BaseQuery):

    def polymorphic_by_searchable_text(self, text_filters=None):
        """Query all Contacts by searchable text.

        If the function of a Persons OrgRole matches, only the matching
        OrgRoles will be returned.

        """
        if text_filters is None:
            text_filters = []
        # we need to join manually instead of using `options.joinedload` to be
        # able to filter by OrgRole.function below.
        query = self.outerjoin(Person.organizations)
        query = query.options(contains_eager(Person.organizations))
        return extend_query_with_textfilter(
            query,
            [Person.firstname, Person.lastname, Organization.name,
             OrgRole.function, Contact.former_contact_id],
            text_filters,
        )

    def get_by_former_contact_id(self, former_contact_id):
        return self.filter_by(former_contact_id=former_contact_id).first()


Contact.query_cls = ContactQuery


class OrganizationQuery(BaseQuery):

    searchable_fields = ['name']

    def get_by_former_contact_id(self, former_contact_id):
        return self.filter_by(former_contact_id=former_contact_id).first()


Organization.query_cls = OrganizationQuery


class ParticipationQuery(BaseQuery):

    def by_dossier(self, dossier):
        return self.filter_by(dossier_oguid=Oguid.for_object(dossier))

    def by_organization(self, organization):
        """Returns both ContactParticapations and OrgRoleParticipation
        of the given organization.
        """
        return self._org_role_join().filter(
            or_(OrgRole.organization == organization,
                ContactParticipation.contact == organization))

    def by_person(self, person):
        """Returns both ContactParticapations and OrgRoleParticipation
        of the given person.
        """
        return self._org_role_join().filter(
            or_(OrgRole.person == person,
                ContactParticipation.contact == person))

    def _org_role_join(self):
        return self.outerjoin(
            OrgRole, OrgRoleParticipation.org_role_id == OrgRole.org_role_id)


Participation.query_cls = ParticipationQuery


class ContactParticipationQuery(ParticipationQuery):

    def by_participant(self, contact):
        return self.filter_by(contact=contact)


ContactParticipation.query_cls = ContactParticipationQuery


class OrgRoleParticipationQuery(ParticipationQuery):

    def by_participant(self, org_role):
        return self.filter_by(org_role=org_role)


OrgRoleParticipation.query_cls = OrgRoleParticipationQuery


class OgdsUserParticipationQuery(ParticipationQuery):

    def by_participant(self, ogds_user):
        return self.filter_by(ogds_userid=ogds_user.id)


OgdsUserParticipation.query_cls = OgdsUserParticipationQuery


class PersonQuery(BaseQuery):

    searchable_fields = ['firstname', 'lastname']

    def get_by_former_contact_id(self, former_contact_id):
        return self.filter_by(former_contact_id=former_contact_id).first()


Person.query_cls = PersonQuery
