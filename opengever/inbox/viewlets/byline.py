from plone.app.layout.viewlets import content
from opengever.mail.behaviors import IMailInAddressMarker, IMailInAddress


class InboxByline(content.DocumentBylineViewlet):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    update = content.DocumentBylineViewlet.update

    def email(self):
        """Gets Email and display it in Byline"""
        if IMailInAddressMarker.providedBy(self.context):
            return IMailInAddress(self.context).get_email_address()
