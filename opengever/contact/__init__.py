from opengever.contact.service import ContactService
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.contact")


def contact_service():
    return ContactService()
