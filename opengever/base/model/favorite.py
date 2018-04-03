from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import ID_LENGTH
from opengever.base.model import PORTAL_TYPE_LENGTH
from opengever.base.model import UID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.base.oguid import Oguid
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class Favorite(Base):

    __tablename__ = 'favorites'

    favorite_id = Column('id', Integer, Sequence("favorites_id_seq"),
                primary_key=True)

    admin_unit_id = Column(String(UNIT_ID_LENGTH), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)

    userid = Column(String(USER_ID_LENGTH), index=True)
    position = Column(Integer, index=True)

    title = Column(String(CONTENT_TITLE_LENGTH), nullable=False)
    is_title_personalized = Column(Boolean, default=False, nullable=False)
    portal_type = Column(String(PORTAL_TYPE_LENGTH))
    icon_class = Column(String(ID_LENGTH))

    plone_uid = Column(String(UID_LENGTH))
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware)
    modified = Column(UTCDateTime(timezone=True),
                      default=utcnow_tz_aware,
                      onupdate=utcnow_tz_aware)


class FavoriteQuery(BaseQuery):

    def is_marked_as_favorite(self, obj, user):
        favorite = self.by_object_and_user(obj, user).first()
        return favorite is not None

    def by_object_and_user(self, obj, user):
        oguid = Oguid.for_object(obj)
        return self.filter_by(oguid=oguid, userid=user.getId())


Favorite.query_cls = FavoriteQuery
