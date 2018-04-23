from opengever.api.favorites import FavoritesGet
from opengever.base.favorite import FavoriteManager
from plone import api
from zExceptions import BadRequest
from zExceptions import Unauthorized


class RepositoryFavoritesGet(FavoritesGet):

    def reply(self):
        userid = self.get_userid()
        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to delete favorites of other users.")

        favorites = FavoriteManager().list_all_repository_favorites(userid)

        return [fav.plone_uid for fav in favorites]

    def get_userid(self):
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply exactly one parameter (user id)")
        return self.params[0]
