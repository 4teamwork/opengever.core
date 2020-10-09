from opengever.readonly import is_in_readonly_mode
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ReadOnlyMessageViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('readonlymessage.pt')

    def available(self):
        return is_in_readonly_mode()
