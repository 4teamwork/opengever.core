from opengever.base.favorite import FavoriteManager
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class FavoritesGet(Service):
    """API Endpoint which returns a list of all favorites for a
    particular user.

    GET /@favorites/peter.mueller HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(FavoritesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid, fav_id = self.read_params()

        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to access favorites of other users.")

        portal_url = api.portal.get().absolute_url()

        if fav_id:
            favorite = Favorite.query.by_userid_and_id(fav_id, userid).first()
            if not favorite:
                # inexistent favorite-id or not ownded by given user
                raise NotFound

            return favorite.serialize(portal_url)
        else:
            favorites = FavoriteManager().list_all(userid)
            return [fav.serialize(portal_url) for fav in favorites]

    def read_params(self):
        if len(self.params) not in [1, 2]:
            raise BadRequest("Must supply user ID as URL and optional "
                             "the favorite id as path parameter.")

        if len(self.params) == 2:
            return self.params

        return self.params[0], None


class FavoritesPost(Service):
    """API Endpoint to add a new favorite for the given oguid and user.

    POST /@favorites/peter.mueller HTTP/1.1
    {
        "oguid": "fd:68398212"
    }

    or

    POST /@favorites/peter.mueller HTTP/1.1
    {
        "UID": "6683982128398212"
    }
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(FavoritesPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid = self.validate_user(self.get_userid())
        data = self.validate_data(json_body(self.request))
        obj = self.lookup_object(data)

        favorite = FavoriteManager().get_favorite(obj, api.user.get_current())
        if favorite:
            # favorite already exists
            self.request.response.setStatus(409)
            return favorite.serialize(api.portal.get().absolute_url())

        favorite = FavoriteManager().add(userid, obj)
        self.request.response.setStatus(201)
        url = favorite.api_url(api.portal.get().absolute_url())
        self.request.response.setHeader('Location', url)

        return favorite.serialize(api.portal.get().absolute_url())

    def lookup_object(dataself, data):
        if data.get('oguid'):
            oguid = Oguid.parse(data.get('oguid'))
            obj = oguid.resolve_object()
        elif data.get('uid'):
            uid = data.get('uid')
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(UID=uid)
            if brains:
                obj = brains[0].getObject()

        if not obj:
            raise BadRequest('Invalid oguid/uid object could not be resolved.')

        return obj

    def validate_data(self, data):
        if not data.get('oguid') and not data.get('uid'):
            raise BadRequest('Missing parameter oguid or uid')
        return data

    def validate_user(self, userid):
        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to add favorites for other users.")
        return userid

    def get_userid(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply user ID as URL path parameters.")
        return self.params[0]


class FavoritesDelete(Service):
    """API Endpoint to delete an existing favorite.

    DELETE /@favorites/peter.mueller/23 HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(FavoritesDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid, fav_id = self.read_params()
        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to delete favorites of other users.")

        FavoriteManager().delete(userid, fav_id)

        self.request.response.setStatus(204)
        return None

    def read_params(self):
        """Returns userid and favorite id, passed in via traversal parameters.
        """
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply exactly two parameters (user id and favorite id)")

        return self.params[0], self.params[1]


class FavoritesPatch(Service):
    """API Endpoint to update an existing favorite.

    PATCH /@favorites/peter.mueller/23 HTTP/1.1
    {
        "title": "Weekly Document",
        "position": 35
    }
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(FavoritesPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid, fav_id = self.read_params()

        if userid != api.user.get_current().getId():
            raise Unauthorized(
                "It's not allowed to update favorites of other users.")

        data = json_body(self.request)
        if data.get('title') is None and data.get('position') is None:
            raise BadRequest('Missing parameter title or position')

        FavoriteManager().update(
            userid, fav_id, title=data.get('title'),
            position=data.get('position'))

        prefer = self.request.getHeader('Prefer')
        if prefer == 'return=representation':
            self.request.response.setStatus(200)
            favorite = Favorite.query.get(fav_id)
            return favorite.serialize(api.portal.get().absolute_url())

        self.request.response.setStatus(204)
        return None

    def read_params(self):
        """Returns userid and favorite id, passed in via traversal parameters.
        """
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply user ID and favorite ID as URL path parameters.")

        return self.params[0], self.params[1]
