from opengever.base import _
from opengever.base import is_favorites_feature_enabled
from opengever.base.handlebars import get_handlebars_template
from pkg_resources import resource_filename
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


class FavoritesMenuViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('favorites_menu.pt')

    @property
    def vuejs_template(self):
        return get_handlebars_template(
            resource_filename('opengever.base.viewlets',
                              'favorites_menu.html'))

    def get_userid(self):
        return api.user.get_current().getId()

    def translations(self):
        return json.dumps({
            'label_overview': translate(
                _(u'label_overview', default=u'Overview'),
                context=self.request),
            'label_no_favorites': translate(
                _(u'label_no_favorites', default=u'No favorites exists.'),
                context=self.request)
        })

    def available(self):
        return is_favorites_feature_enabled()
