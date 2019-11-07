from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.docprops import OrgRoleAddressDocPropertyProvider
from opengever.contact.docprops import OrgRoleDocPropertyProvider
from opengever.base.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class OrgRoleAddress(object):
    """Represents the addresses of a person at an organization.

    Provide the same interface as Address.

    """
    def __init__(self, person, organization, organization_address):
        self.person = person
        self.organization = organization
        self.organization_address = organization_address

    def __eq__(self, other):
        if isinstance(other, OrgRoleAddress):
            return other.address_id == self.address_id
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash(self.address_id)

    @property
    def address_id(self):
        return u'org_role_address:{}'.format(
            self.organization_address.address_id)

    @property
    def street(self):
        return self.organization_address.street

    @property
    def zip_code(self):
        return self.organization_address.zip_code

    @property
    def city(self):
        return self.organization_address.city

    @property
    def country(self):
        return self.organization_address.country

    def get_lines(self):
        return filter(None, [
            self.person.get_title(),
            self.organization.get_title(),
            self.street,
            u" ".join(filter(None,
                      [self.zip_code, self.city])),
            self.country,
        ])

    def get_doc_property_provider(self):
        return OrgRoleAddressDocPropertyProvider(self)


class OrgRole(Base):

    __tablename__ = 'org_roles'

    org_role_id = Column("id", Integer,
                         Sequence("org_roles_id_seq"),
                         primary_key=True)

    person_id = Column(Integer, ForeignKey('persons.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'))

    organization = relationship("Organization", back_populates="persons")
    person = relationship("Person", back_populates="organizations")

    function = Column(String(CONTENT_TITLE_LENGTH))
    department = Column(String(CONTENT_TITLE_LENGTH))
    description = Column(UnicodeCoercingText)

    participations = relationship("OrgRoleParticipation",
                                  back_populates="org_role")

    @property
    def id(self):
        return self.org_role_id

    @property
    def is_adapted_user(self):
        return False

    @property
    def addresses(self):
        return [OrgRoleAddress(self.person, self.organization, address)
                for address in self.organization.addresses]

    @property
    def mail_addresses(self):
        return self.person.mail_addresses + self.organization.mail_addresses

    @property
    def phonenumbers(self):
        return self.person.phonenumbers + self.organization.phonenumbers

    @property
    def urls(self):
        return self.person.urls + self.organization.urls

    def get_title(self, with_former_id=False):
        title = u'{} - {}'.format(
            self.person.get_title(with_former_id=with_former_id),
            self.organization.get_title())

        if self.function or self.department:
            suffix = u' - '.join(filter(
                lambda each: each, [self.function, self.department]))
            title = u'{} ({})'.format(title, suffix)

        return title

    def get_url(self, view='view'):
        return self.person.get_url()

    def get_css_class(self):
        return self.person.get_css_class()

    def get_contact_id(self):
        """Returns the id of the person that is represented by the Orgrole.
        """
        return self.person.contact_id

    def get_doc_property_provider(self):
        return OrgRoleDocPropertyProvider(self)
