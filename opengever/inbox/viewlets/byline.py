"""Defines a customized byline for inbox"""
from plone.app.layout.viewlets import content
from opengever.mail.behaviors import IMailInAddressMarker, IMailInAddress
from opengever.base.browser.helper import get_css_class


class InboxByline(content.DocumentBylineViewlet):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)


    def email(self):
        """Gets Email and display it in Byline"""
        if IMailInAddressMarker.providedBy(self.context):
            return IMailInAddress(self.context).get_email_address()
