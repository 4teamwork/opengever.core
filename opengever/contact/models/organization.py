from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.contact import Contact
from opengever.contact.utils import get_contactfolder_url
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Organization(Contact):

    __tablename__ = 'organizations'

    organization_id = Column('id', Integer,
                             ForeignKey('contacts.id'), primary_key=True)
    name = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    persons = relationship("OrgRole", back_populates="organization")

    __mapper_args__ = {'polymorphic_identity': 'organization'}

    @property
    def wrapper_id(self):
        return 'organization-{}'.format(self.organization_id)

    def get_url(self, view='view'):
        return '{}/{}/{}'.format(
            get_contactfolder_url(), self.wrapper_id, view)

    def get_title(self):
        return self.name

    def get_css_class(self):
        return 'contenttype-organization'
