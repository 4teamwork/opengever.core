from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import FIRSTNAME_LENGTH
from opengever.base.model import LASTNAME_LENGTH
from opengever.contact.docprops import PersonDocPropertyProvider
from opengever.contact.models.contact import Contact
from opengever.contact.utils import get_contactfolder_url
from opengever.contact.wrapper import PersonWrapper
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Person(Contact):

    __tablename__ = 'persons'

    person_id = Column('id', Integer,
                       ForeignKey('contacts.id'), primary_key=True)
    salutation = Column(String(CONTENT_TITLE_LENGTH))
    academic_title = Column(String(CONTENT_TITLE_LENGTH))
    firstname = Column(String(FIRSTNAME_LENGTH), nullable=False)
    lastname = Column(String(LASTNAME_LENGTH), nullable=False)

    organizations = relationship("OrgRole", back_populates="person")

    __mapper_args__ = {'polymorphic_identity': 'person'}

    @property
    def fullname(self):
        return u'{} {}'.format(self.lastname, self.firstname)

    @property
    def wrapper_id(self):
        return 'contact-{}'.format(self.person_id)

    def get_wrapper(self, context):
        return PersonWrapper.wrap(context, self)

    def get_url(self, view='view'):
        return '{}/{}/{}'.format(
            get_contactfolder_url(), self.wrapper_id, view)

    def get_title(self, with_former_id=False):
        if with_former_id and self.former_contact_id:
            return u'{} [{}]'.format(self.fullname, self.former_contact_id)

        return self.fullname

    def get_css_class(self):
        return 'contenttype-person'

    def get_doc_property_provider(self):
        return PersonDocPropertyProvider(self)
