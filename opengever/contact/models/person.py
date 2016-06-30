from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.contact import Contact
from opengever.ogds.models import FIRSTNAME_LENGTH
from opengever.ogds.models import LASTNAME_LENGTH
from opengever.ogds.models.types import UnicodeCoercingText
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
    description = Column(UnicodeCoercingText)

    organisations = relationship("OrgRole", back_populates="person")

    __mapper_args__ = {'polymorphic_identity':'person'}
