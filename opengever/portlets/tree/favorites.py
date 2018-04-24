from opengever.base.favorite import FavoriteManager
from plone import api
from plone.app.caching.interfaces import IETagValue
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IETagValue)
@adapter(Interface, Interface)
class RepositoryFavoritesETagValue(object):

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        if api.user.is_anonymous():
            # Anonymous users can't have repository favorites - short circuit
            # cache key generation, no need to ask the view
            return ''

        favorites = FavoriteManager().list_all_repository_favorites(
            api.user.get_current().getId())

        if not favorites:
            return ''

        return '-'.join([
            str(len(favorites)),
            max(fav.modified.strftime('%s') for fav in favorites)
            ])
