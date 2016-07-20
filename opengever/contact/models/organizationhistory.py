from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.contacthistory import ContactHistory
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class OrganizationHistory(ContactHistory):

    __tablename__ = 'organizationshistory'

    organization_history_id = Column(
        'id', Integer,
        ForeignKey('contactshistory.id'), primary_key=True)
    name = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'organizationhistory'}
