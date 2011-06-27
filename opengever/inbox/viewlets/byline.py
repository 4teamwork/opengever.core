"""Defines a customized byline for inbox"""
from plone.app.layout.viewlets import content
from opengever.mail.behaviors import IMailInAddressMarker, IMailInAddress
from opengever.base.browser.helper import css_class_from_obj


class InboxByline(content.DocumentBylineViewlet):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    update = content.DocumentBylineViewlet.update

    def css_class_from_obj(self):
        return css_class_from_obj(self.context)

    
    def email(self):
        """Gets Email and display it in Byline"""
        if IMailInAddressMarker.providedBy(self.context):
            return IMailInAddress(self.context).get_email_address()
