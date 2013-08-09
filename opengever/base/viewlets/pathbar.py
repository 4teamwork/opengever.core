from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common


class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('pathbar.pt')
