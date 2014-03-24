"""Defines a customized byline for inbox"""
from ftw.mail.interfaces import IEmailAddress
from opengever.base.browser.helper import get_css_class
from plone.app.layout.viewlets import content


class InboxByline(content.DocumentBylineViewlet):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)


    def email(self):
        """Gets Email and display it in Byline"""
        mail_address = IEmailAddress(self.request
            ).get_email_for_object(self.context)
        return mail_address
