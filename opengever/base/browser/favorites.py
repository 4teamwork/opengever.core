from opengever.base import _
from opengever.base.handlebars import get_handlebars_template
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json
import os


class ManageFavoritesView(BrowserView):

    template = ViewPageTemplateFile('templates/favorites.pt')

    @property
    def vuejs_template(self):
        return get_handlebars_template(os.path.join(os.path.dirname(__file__),
                                                    'templates',
                                                    'favorites_list.html'))

    def __call__(self):
        return self.template()

    def get_userid(self):
        return api.user.get_current().getId()

    def translations(self):

        return json.dumps({
            'label_title': translate(_('Titel'), context=self.request),
        })
