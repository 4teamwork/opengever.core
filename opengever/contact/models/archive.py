from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declared_attr


class ArchiveMixin(object):

    @declared_attr
    def contact_id(self):
        return Column(Integer, ForeignKey('contacts.id'), nullable=False)

    actor_id = Column(String(USER_ID_LENGTH), nullable=False)
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware)
