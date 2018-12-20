from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import FIRSTNAME_LENGTH
from opengever.base.model import LASTNAME_LENGTH
from opengever.contact.models.archivedcontact import ArchivedContact
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class ArchivedPerson(ArchivedContact):

    __tablename__ = 'archived_persons'

    archived_person_id = Column(
        'id', Integer,
        ForeignKey('archived_contacts.id'), primary_key=True)
    salutation = Column(String(CONTENT_TITLE_LENGTH))
    academic_title = Column(String(CONTENT_TITLE_LENGTH))
    firstname = Column(String(FIRSTNAME_LENGTH), nullable=False)
    lastname = Column(String(LASTNAME_LENGTH), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'archived_person'}

    @property
    def fullname(self):
        return u'{} {}'.format(self.firstname, self.lastname)
