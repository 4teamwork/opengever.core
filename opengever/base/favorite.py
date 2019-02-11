from opengever.base.browser.helper import get_css_class
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from plone.uuid.interfaces import IUUID
from sqlalchemy import and_
from zExceptions import NotFound


class FavoriteManager(object):

    def delete(self, userid, fav_id):
        favorite = Favorite.query.by_userid_and_id(fav_id, userid).first()
        if not favorite:
            # inexistent favorite-id or not ownded by given user
            raise NotFound

        # update positions
        favorites_to_reduce = Favorite.query.by_userid(userid).filter(
            Favorite.position > favorite.position).with_for_update().order_by(
                Favorite.position)

        for new_pos, fav_to_reduce in enumerate(
                favorites_to_reduce, start=favorite.position):
            fav_to_reduce.position = new_pos

        create_session().delete(favorite)

    def add(self, userid, obj):
        truncated_title = Favorite.truncate_title(obj.Title().decode('utf-8'))
        favorite = Favorite(
            userid=userid,
            oguid=Oguid.for_object(obj),
            title=truncated_title,
            portal_type=obj.portal_type,
            icon_class=get_css_class(obj),
            plone_uid=IUUID(obj),
            position=self.get_next_position(userid))

        create_session().add(favorite)
        create_session().flush()
        return favorite

    def get_next_position(self, userid):
        position = Favorite.query.get_highest_position(userid)
        if position is None:
            return 0

        return position + 1

    def update(self, userid, fav_id, title, position):
        favorite = Favorite.query.by_userid_and_id(fav_id, userid).first()
        if not favorite:
            # inexistent favorite-id or not ownded by given user
            raise NotFound

        if title:
            favorite.title = title
            favorite.is_title_personalized = True

        if position is not None:
            self.update_position(favorite, position, userid)

        return favorite

    def update_position(self, fav_to_updated, position, userid):
        """Update the position all favorites affected by the reordering."""
        old_position = fav_to_updated.position

        if old_position == position:
            return
        elif old_position < position:
            # move down
            favorites_to_reduce = Favorite.query.by_userid(userid).filter(
                and_(Favorite.position > old_position,
                     Favorite.position <= position)).with_for_update()
            for favorite in favorites_to_reduce:
                favorite.position = favorite.position - 1
        else:
            # move up
            favorites_to_raise = Favorite.query.by_userid(userid).filter(
                and_(Favorite.position >= position,
                     Favorite.position < old_position)).with_for_update()
            for favorite in favorites_to_raise:
                favorite.position = favorite.position + 1

        fav_to_updated.position = position

    def list_all(self, userid):
        return Favorite.query.by_userid(userid=userid).all()

    def list_all_repository_favorites(self, userid):
        favorites = Favorite.query.only_repository_favorites(
            userid, get_current_admin_unit().id()).all()
        return favorites

    def get_favorite(self, obj, user):
        return Favorite.query.by_object_and_user(obj, user).first()

    def get_repository_favorites_cache_key(self, userid):
        favorites = self.list_all_repository_favorites(userid)

        if not favorites:
            return ''

        return '-'.join([
            str(len(favorites)),
            max(fav.modified.strftime('%s') for fav in favorites)
            ])
