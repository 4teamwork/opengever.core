from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.ogds.models.query import BaseQuery
from opengever.ogds.models.query import extend_query_with_textfilter
from sqlalchemy.orm import contains_eager


class ContactQuery(BaseQuery):

    def polymorphic_by_searchable_text(self, text_filters=[]):
        """Query all Contacts by searchable text.

        If the function of a Persons OrgRole matches, only the matching
        OrgRoles will be returned.

        """
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
