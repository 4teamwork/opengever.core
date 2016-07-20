from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.contacthistory import ContactHistory
from opengever.ogds.models import FIRSTNAME_LENGTH
from opengever.ogds.models import LASTNAME_LENGTH
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class PersonHistory(ContactHistory):

    __tablename__ = 'personshistory'

    person_history_id = Column(
        'id', Integer,
        ForeignKey('contactshistory.id'), primary_key=True)
    salutation = Column(String(CONTENT_TITLE_LENGTH))
    academic_title = Column(String(CONTENT_TITLE_LENGTH))
    firstname = Column(String(FIRSTNAME_LENGTH), nullable=False)
    lastname = Column(String(LASTNAME_LENGTH), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'personhistory'}
