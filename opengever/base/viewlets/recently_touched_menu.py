from opengever.base import _
from opengever.base.handlebars import get_handlebars_template
from pkg_resources import resource_filename
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


class RecentlyTouchedMenuViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('recently_touched_menu.pt')

    @property
    def vuejs_template(self):
        return get_handlebars_template(
            resource_filename('opengever.base.viewlets',
                              'recently_touched_menu.html'))

    def get_userid(self):
        return api.user.get_current().getId()

    def available(self):
        return True

    def get_num_checked_out(self):
        current_user_id = api.user.get_current().getId()
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(
            portal_type='opengever.document.document',
            checked_out=current_user_id)
        return len(brains)

    def translations(self):
        return json.dumps({
            'label_no_checked_out_docs': translate(
                _(u'label_no_checked_out_docs',
                  default=u'No checked out documents'),
                context=self.request),
            'label_no_recently_touched_docs': translate(
                _(u'label_no_recently_touched_docs',
                  default=u'No recently touched documents yet'),
                context=self.request),
            'label_checked_out': translate(
                _(u'label_checked_out',
                  default=u'Checked out'),
                context=self.request),
            'label_recently_touched': translate(
                _(u'label_recently_touched',
                  default=u'Recently touched'),
                context=self.request),
        })
