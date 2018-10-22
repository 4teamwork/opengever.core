from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class View(BrowserView):

    template = ViewPageTemplateFile('templates/notification_mail_macros.pt')
