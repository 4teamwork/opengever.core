from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact.models.archivedcontact import ArchivedContact
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class ArchivedOrganization(ArchivedContact):

    __tablename__ = 'archived_organizations'

    archived_organization_id = Column(
        'id', Integer,
        ForeignKey('archived_contacts.id'), primary_key=True)
    name = Column(String(CONTENT_TITLE_LENGTH), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'archived_organization'}
