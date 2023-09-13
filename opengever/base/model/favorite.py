from opengever.base.browser.helper import get_css_class
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import CSS_CLASS_LENGTH
from opengever.base.model import FILENAME_LENGTH
from opengever.base.model import PORTAL_TYPE_LENGTH
from opengever.base.model import UID_LENGTH
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.base.model import WORKFLOW_STATE_LENGTH
from opengever.base.oguid import Oguid
from opengever.base.query import BaseQuery
from opengever.base.sentry import log_msg_to_sentry
from opengever.bumblebee import is_bumblebeeable
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.utils import supports_is_subdossier
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.repository.interfaces import IRepositoryFolder
from opengever.workspaceclient import is_workspace_client_feature_enabled
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFCore.WorkflowCore import WorkflowException
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
import logging
import os.path


logger = logging.getLogger('opengever.base')


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
    filename = Column(String(FILENAME_LENGTH))

    plone_uid = Column(String(UID_LENGTH))
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware)
    modified = Column(UTCDateTime(timezone=True),
                      default=utcnow_tz_aware,
                      onupdate=utcnow_tz_aware)

    review_state = Column(String(WORKFLOW_STATE_LENGTH))
    is_subdossier = Column(Boolean, nullable=True)
    is_leafnode = Column(Boolean, nullable=True)

    @classmethod
    def create(cls, userid, obj, **kwargs):
        truncated_title = cls.truncate_title(obj.Title().decode('utf-8'))

        is_subdossier = None
        if supports_is_subdossier(obj):
            is_subdossier = obj.is_subdossier()

        is_leafnode = None
        if IRepositoryFolder.providedBy(obj):
            is_leafnode = obj.is_leaf_node()

        filename = None
        if IBaseDocument.providedBy(obj):
            filename = obj.get_filename()

        review_state = None
        try:
            review_state = api.content.get_state(obj)
        except WorkflowException:
            log_msg_to_sentry(
                "Could not retrieve object workflow state while creating "
                "favorite.",
                extra={'failing_object': repr(obj)})

        params = dict(
            userid=userid,
            oguid=Oguid.for_object(obj),
            title=truncated_title,
            filename=filename,
            portal_type=obj.portal_type,
            icon_class=get_css_class(obj),
            plone_uid=IUUID(obj),
            position=cls.query.get_next_position(userid),
            review_state=review_state,
            is_subdossier=is_subdossier,
            is_leafnode=is_leafnode,
        )
        params.update(kwargs)
        return cls(**params)

    def serialize(self, portal_url, resolve=False):
        """Serializes a favorite.

        Favorites are unresolved by default. The `target_url` contains a link
        to resolve a favorite. Resolving a favorite means, we lookup the favorite
        object by its oguid.

        The serializer can also return already resolved favorites. The target url
        will then contain the url to the object itself.

        If the favorite cannot be resolved, i.e. because it does not exist on the
        current admin-unit, the unresolved favorite will be returned instead.
        """
        resolved_obj = None

        if resolve:
            try:
                resolved_obj = self.oguid.resolve_object()
            except InvalidOguidIntIdPart:
                logger.warn('Failed to resolve Oguid %s', self.oguid.id)

        result = {
            '@id': self.api_url(portal_url),
            'portal_type': self.portal_type,
            'favorite_id': self.favorite_id,
            'oguid': self.oguid.id,
            'uid': self.plone_uid,
            'title': self.title,
            'filename': self.filename,
            'icon_class': self.icon_class,
            'target_url': self.get_target_url(resolved_obj),
            'tooltip_url': self.get_tooltip_url(),
            'position': self.position,
            'admin_unit': AdminUnit.query.get(self.admin_unit_id).title,
            'review_state': self.review_state,
            'is_subdossier': self.is_subdossier,
            'is_leafnode': self.is_leafnode,
            'resolved': bool(resolved_obj)
        }

        if resolved_obj and IDossierMarker.providedBy(resolved_obj):
            result['dossier_type'] = IDossier(resolved_obj).dossier_type

        if is_workspace_client_feature_enabled() and IBaseDocument.providedBy(resolved_obj):
            result['is_locked_by_copy_to_workspace'] = resolved_obj.is_locked_by_copy_to_workspace()

        return result

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

    def get_target_url(self, resolved_obj=None):
        if resolved_obj:
            return resolved_obj.absolute_url()

        admin_unit = AdminUnit.query.get(self.admin_unit_id)
        return u'{}/resolve_oguid/{}'.format(admin_unit.public_url, self.oguid)

    @staticmethod
    def truncate_title(title):
        return safe_unicode(title)[:CONTENT_TITLE_LENGTH]

    @staticmethod
    def truncate_filename(filename):
        if not filename:
            return filename

        # try to preserve extension while truncating
        root, ext = os.path.splitext(safe_unicode(filename))
        preserved_ext = root[:FILENAME_LENGTH - len(ext)] + ext
        if len(preserved_ext) <= FILENAME_LENGTH:
            return preserved_ext

        # but mercilessly truncate as a fallback to handle very long extensions
        # most likely the file has no "real" extension but a dot in its name
        # somewhere
        return filename[:FILENAME_LENGTH]


class FavoriteQuery(BaseQuery):

    def get_next_position(self, userid):
        position = self.get_highest_position(userid)
        if position is None:
            return 0

        return position + 1

    def is_marked_as_favorite(self, obj, user):
        favorite = self.by_object_and_user(obj, user).first()
        return favorite is not None

    def by_object(self, obj):
        oguid = Oguid.for_object(obj)
        return self.filter_by(oguid=oguid)

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

    def update_review_state(self, obj):
        query = self.by_object(obj)
        review_state = api.content.get_state(obj)
        query.update({'review_state': review_state})

    def update_is_subdossier(self, obj):
        if not supports_is_subdossier(obj):
            return
        query = self.by_object(obj)
        query.update({'is_subdossier': obj.is_subdossier()})

    def update_is_leafnode(self, obj):
        if not IRepositoryFolder.providedBy(obj):
            return
        query = self.by_object(obj)
        query.update({'is_leafnode': obj.is_leaf_node()})

    def update_filename(self, obj):
        if not IBaseDocument.providedBy(obj):
            return
        new_filename = obj.get_filename()
        truncated_filename = Favorite.truncate_filename(new_filename)
        query = self.by_object(obj)
        query.update({'filename': truncated_filename})


Favorite.query_cls = FavoriteQuery
