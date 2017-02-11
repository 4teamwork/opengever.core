from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import LogoViewlet


class LogoViewlet(LogoViewlet):

    index = ViewPageTemplateFile('logo.pt')
