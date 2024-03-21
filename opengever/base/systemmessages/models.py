from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.base.types import UnicodeCoercingText
from opengever.ogds.base.utils import get_current_admin_unit
from plone.restapi.interfaces import ISerializeToJson
from sqlalchemy import and_
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy.orm import relationship
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


tables = [
    'system_messages',
]


class SystemMessage(Base):

    __tablename__ = 'system_messages'

    id = Column(Integer, Sequence('system_message_id_seq'), primary_key=True)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=True)
    admin_unit = relationship('AdminUnit', foreign_keys=[admin_unit_id])
    text_en = Column(UnicodeCoercingText, nullable=True)
    text_de = Column(UnicodeCoercingText, nullable=True)
    text_fr = Column(UnicodeCoercingText, nullable=True)
    start_ts = Column(UTCDateTime(timezone=True), nullable=False)
    end_ts = Column(UTCDateTime(timezone=True), nullable=False)
    type = Column(String(30), nullable=False)

    @classmethod
    def query_active_msgs(cls):
        """Retrieves active system messages for the current admin unit or

        messages with no admin unit assigned admin_unit_id = None.
        Returns:list: A list containing  active system messages.
        """
        local_unit_id = get_current_admin_unit().unit_id

        query = cls.query
        query = query.filter(cls.admin_unit_id == local_unit_id)
        query = query.filter(and_(cls.start_ts <= utcnow_tz_aware(), utcnow_tz_aware() <= cls.end_ts))
        system_msgs = []
        for sys_msg in query:
            sys_msg_json = getMultiAdapter((sys_msg, getRequest()), ISerializeToJson)()
            system_msgs.append(sys_msg_json)

        return system_msgs

    def is_active(self):
        return self.start_ts <= utcnow_tz_aware() <= self.end_ts
