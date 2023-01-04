from opengever.base.query import BaseQuery
from opengever.base.query import extend_query_with_textfilter
from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.contact.models import Person


class ContactQuery(BaseQuery):

    def polymorphic_by_searchable_text(self, text_filters=None):
        """Query all Contacts by searchable text.

        If the function of a Persons OrgRole matches, only the matching
        OrgRoles will be returned.

        """
        if text_filters is None:
            text_filters = []

        query = Contact.query
        return extend_query_with_textfilter(
            query,
            [Person.firstname, Person.lastname, Organization.name,
             Contact.former_contact_id],
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


class PersonQuery(BaseQuery):

    searchable_fields = ['firstname', 'lastname']

    def get_by_former_contact_id(self, former_contact_id):
        return self.filter_by(former_contact_id=former_contact_id).first()


Person.query_cls = PersonQuery
