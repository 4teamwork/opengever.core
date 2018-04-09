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
            'label_title': translate(_(u'label_title', default=u'Title'),
                                     context=self.request),
            'label_save': translate(_(u'Save', default=u'Save'),
                                    context=self.request),
            'label_cancel': translate(_(u'label_cancel', default=u'Cancel'),
                                      context=self.request),
            'message_title': translate(_(u'message_title_error', default=u'Error'),
                                       context=self.request),
            'message_not_saved': translate(_(u'message_not_saved',
                                             default='Change could not be saved.'),
                                           context=self.request),

        })
