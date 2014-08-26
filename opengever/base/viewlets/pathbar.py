from opengever.ogds.base.utils import get_current_admin_unit
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('pathbar.pt')

    def admin_unit_label(self):
        return get_current_admin_unit().label()
