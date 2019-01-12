from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import CSS_CLASS_LENGTH
from opengever.base.model import PORTAL_TYPE_LENGTH
from opengever.base.model import UID_LENGTH
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.base.oguid import Oguid
from opengever.base.query import BaseQuery
from opengever.bumblebee import is_bumblebeeable
from opengever.ogds.models.admin_unit import AdminUnit
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import and_
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class Favorite(Base):

    __tablename__ = 'favorites'
    __table_args__ = (
        UniqueConstraint('admin_unit_id', 'int_id', 'userid',
                         name='ix_favorites_unique'),
        {})

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
    icon_class = Column(String(CSS_CLASS_LENGTH))

    plone_uid = Column(String(UID_LENGTH))
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware)
    modified = Column(UTCDateTime(timezone=True),
                      default=utcnow_tz_aware,
                      onupdate=utcnow_tz_aware)

    def serialize(self, portal_url):
        return {
            '@id': self.api_url(portal_url),
            'portal_type': self.portal_type,
            'favorite_id': self.favorite_id,
            'oguid': self.oguid.id,
            'title': self.title,
            'icon_class': self.icon_class,
            'target_url': self.get_target_url(),
            'tooltip_url': self.get_tooltip_url(),
            'position': self.position,
            'admin_unit': AdminUnit.query.get(self.admin_unit_id).title}

    def api_url(self, portal_url):
        return '{}/@favorites/{}/{}'.format(
            portal_url, self.userid, self.favorite_id)

    @property
    def tooltip_view(self):
        if is_bumblebeeable(self):
            return 'tooltip'

    def get_tooltip_url(self):
        url = self.get_target_url()
        if self.tooltip_view:
            return u'{}/{}'.format(url, self.tooltip_view)

        return None

    def get_target_url(self):
        admin_unit = AdminUnit.query.get(self.admin_unit_id)
        return u'{}/resolve_oguid/{}'.format(admin_unit.public_url, self.oguid)

    @staticmethod
    def truncate_title(title):
        return safe_unicode(title)[:CONTENT_TITLE_LENGTH]


class FavoriteQuery(BaseQuery):

    def is_marked_as_favorite(self, obj, user):
        favorite = self.by_object_and_user(obj, user).first()
        return favorite is not None

    def by_object_and_user(self, obj, user):
        oguid = Oguid.for_object(obj)
        return self.filter_by(oguid=oguid, userid=user.getId())

    def by_userid(self, userid):
        return self.filter_by(userid=userid)

    def by_userid_and_id(self, fav_id, userid):
        return Favorite.query.filter(
            and_(Favorite.favorite_id == fav_id, Favorite.userid == userid))

    def get_highest_position(self, userid):
        return self.session.query(
            func.max(Favorite.position)).filter_by(userid=userid).scalar()

    def only_repository_favorites(self, userid, admin_unit_id):
        query = self.by_userid(userid)
        query = query.filter_by(
            portal_type='opengever.repository.repositoryfolder')
        return query.filter_by(admin_unit_id=admin_unit_id)

    def update_title(self, new_title):
        truncated_title = Favorite.truncate_title(new_title)
        self.update({'title': truncated_title})


Favorite.query_cls = FavoriteQuery
