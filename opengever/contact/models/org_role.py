from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.docprops import OrgRoleDocPropertyProvider
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

    def get_doc_property_provider(self, prefix):
        return OrgRoleDocPropertyProvider(self, prefix)
