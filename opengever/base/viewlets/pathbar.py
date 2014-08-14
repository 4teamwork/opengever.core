from opengever.ogds.base.utils import get_current_org_unit
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('pathbar.pt')

    def org_unit_label(self):
        return get_current_org_unit().label()
