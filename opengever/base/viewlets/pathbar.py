from opengever.ogds.base.utils import get_current_client
from plone.app.layout.viewlets import common
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('pathbar.pt')

    def client_title(self):
        try:
            return get_current_client().title
        except ValueError:
            # Current client was not found we return the default home label
            return pmf('tabs_home', default="Home")
