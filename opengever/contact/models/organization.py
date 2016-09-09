from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.docprops import OrganizationDocPropertProvider
from opengever.contact.models.contact import Contact
from opengever.contact.utils import get_contactfolder_url
from opengever.contact.wrapper import OrganizationWrapper
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class OrganizationQuery(BaseQuery):

    searchable_fields = ['name']

    def get_by_former_contact_id(self, former_contact_id):
        return self.filter_by(former_contact_id=former_contact_id).first()


class Organization(Contact):

    __tablename__ = 'organizations'

    organization_id = Column('id', Integer,
                             ForeignKey('contacts.id'), primary_key=True)
    name = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    persons = relationship("OrgRole", back_populates="organization")

    __mapper_args__ = {'polymorphic_identity': 'organization'}

    @property
    def wrapper_id(self):
        return 'contact-{}'.format(self.organization_id)

    def get_wrapper(self, context):
        return OrganizationWrapper.wrap(context, self)

    def get_url(self, view='view'):
        return '{}/{}/{}'.format(
            get_contactfolder_url(), self.wrapper_id, view)

    def get_title(self, with_former_id=False):
        if with_former_id and self.former_contact_id:
            return u'{} [{}]'.format(self.name, self.former_contact_id)

        return self.name

    def get_css_class(self):
        return 'contenttype-organization'

    def get_doc_property_provider(self, prefix):
        return OrganizationDocPropertProvider(self, prefix)

Organization.query_cls = OrganizationQuery
