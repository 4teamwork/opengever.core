from opengever.base.favorite import FavoriteManager
from opengever.base.oguid import Oguid
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class FavoritesGet(Service):
    """API Endpoint which returns a list of all favorites.

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
        return [fav.serialize() for fav in
                FavoriteManager().list_all(self.get_userid())]

    def get_userid(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (user id)")
        return self.params[0]


class FavoritesPost(Service):
    """API Endpoint to add a new favorite for the given oguid.

    POST /@favorites/peter.mueller HTTP/1.1
    {
        "oguid": "fd:68398212"
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
        data = json_body(self.request)
        if not data.get('oguid'):
            raise Exception('Missing parameter oguid')

        oguid = Oguid.parse(data.get('oguid'))
        obj = oguid.resolve_object()
        if not obj:
            raise Exception('Invalid oguid, could not be resolved.')

        favorite = FavoriteManager().add(self.get_userid(), obj)
        return favorite.serialize()

    def get_userid(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (user id)")
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
        FavoriteManager().delete(userid, fav_id)

    def read_params(self):
        """Returns userid and favorite id, passed in via traversal parameters.
        """
        if len(self.params) == 1:
            raise Exception(
                "Must supply exactly two parameter (user id and favorite id)")

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

        data = json_body(self.request)
        if data.get('title') is None and data.get('position') is None:
            raise Exception('Missing parameter title or position')

        FavoriteManager().update(
            userid, fav_id, title=data.get('title'),
            position=data.get('position'), is_title_personalized=True)

    def read_params(self):
        """Returns userid and favorite id, passed in via traversal parameters.
        """
        if len(self.params) == 1:
            raise Exception(
                "Must supply exactly two parameter (user id and favorite id)")

        return self.params[0], self.params[1]
