from opengever.api.favorites import FavoritesDelete
from opengever.api.favorites import FavoritesGet
from opengever.api.favorites import FavoritesPost
from opengever.base.favorite import FavoriteManager
from plone import api
from plone.app.uuid.utils import uuidToObject
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


class RepositoryFavoritesPost(FavoritesPost):
    """API Endpoint to add a new favorite for the given UID and user.

    POST /@repository-favorites/peter.mueller HTTP/1.1
    {
        "uuid": "967775b9b9094446950eef8e2a35d42d"
    }
    """
    def lookup_object(dataself, data):
        obj = uuidToObject(data.get('uuid'))
        if not obj:
            raise BadRequest('Invalid uuid, could not be resolved.')
        return obj

    def validate_data(self, data):
        if not data.get('uuid'):
            raise BadRequest('Missing parameter uuid')
        return data


class RepositoryFavoritesDelete(FavoritesDelete):
    """API Endpoint to delete an existing favorite.

    DELETE /@repository-favorites/peter.mueller/967775b9b9094446950eef8e2a35d42d HTTP/1.1
    """

    def read_params(self):
        """Returns userid and favorite id looked-up from the uuid, passed
        in via traversal parameters.
        """
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply exactly two parameters (user id and uuid)")

        return self.params[0], self.lookup_fav_id(self.params[1])

    def lookup_fav_id(self, uuid):
        obj = uuidToObject(uuid)
        favorite = FavoriteManager().get_favorite(obj, api.user.get_current())

        return favorite.favorite_id if favorite else ''
