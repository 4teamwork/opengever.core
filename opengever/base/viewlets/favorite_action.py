from opengever.base import is_favorites_feature_enabled
from opengever.base.favorite import FavoriteManager
from opengever.base.oguid import Oguid
from plone import api
from plone.app.caching.interfaces import IETagValue
from plone.app.layout.viewlets import common
from plone.dexterity.interfaces import IDexterityContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class FavoriteAction(common.ViewletBase):

    index = ViewPageTemplateFile('favorite_action.pt')

    def get_favorite(self):
        return FavoriteManager().get_favorite(
            self.context, api.user.get_current())

    def oguid(self):
        return Oguid.for_object(self.context)

    def url(self):
        return '{}/@favorites/{}'.format(
            api.portal.get().absolute_url(), api.user.get_current().getId())

    def available(self):
        if not is_favorites_feature_enabled():
            return False

        return IDexterityContent.providedBy(self.context) and self.oguid()


class FavoriteETagValue(object):
    implements(IETagValue)
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        favorite = FavoriteManager().get_favorite(
            self.published.context, api.user.get_current())

        if not favorite:
            return None

        return str(favorite.favorite_id)
