from opengever.base.favorite import FavoriteManager
from plone.restapi.services import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RepositoryFavoritesGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RepositoryFavoritesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def reply(self):
        favorites = FavoriteManager().list_all_repository_favorites(
            self.get_userid())

        return [fav.plone_uid for fav in favorites]

    def get_userid(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (user id)")
        return self.params[0]
