from opengever.base.favorite import FavoriteManager
from opengever.base.oguid import Oguid
from plone import api
from plone.app.layout.viewlets import common
from plone.dexterity.interfaces import IDexterityContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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
        return IDexterityContent.providedBy(self.context) and self.oguid()
