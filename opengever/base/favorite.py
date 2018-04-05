from opengever.base.browser.helper import get_css_class
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from plone.uuid.interfaces import IUUID


class FavoriteManager(object):

    def delete(self, userid, fav_id):
        favorite = Favorite.query.get(fav_id)

        if not favorite:
            raise Exception(
                u'Favorite with the id {} does not exist.'.format(fav_id))

        if userid != favorite.userid:
            raise Exception(
                u'Parameter missmatch: Favorite {} is not owned by {}'.format(
                    fav_id, userid))

        create_session().delete(favorite)

    def add(self, userid, obj):
        favorite = Favorite(
            userid=userid,
            oguid=Oguid.for_object(obj),
            title=obj.title,
            portal_type=obj.portal_type,
            icon_class=get_css_class(obj),
            plone_uid=IUUID(obj))

        create_session().add(favorite)
        return favorite

    def update(self, userid, fav_id, title, position, is_title_personalized=False):
        favorite = Favorite.query.get(fav_id)

        if not favorite:
            raise Exception(
                u'Favorite with the id {} does not exist.'.format(fav_id))

        if userid != favorite.userid:
            raise Exception(
                u'Parameter missmatch: Favorite {} is not owned by {}'.format(
                    fav_id, userid))

        if title:
            favorite.title = title
            favorite.is_title_personalized = is_title_personalized

        if position:
            favorite.position = position

        return favorite

    def list_all(self, userid):
        return Favorite.query.by_userid(userid=userid).all()

    def list_all_repository_favorites(self, userid):
        favorites = Favorite.query.only_repository_favorites(
            userid, get_current_admin_unit().id()).all()
        return favorites
