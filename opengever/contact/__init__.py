from zope.i18nmessageid import MessageFactory
from opengever.contact.service import ContactService
_ = MessageFactory("opengever.contact")


def contact_service():
    return ContactService()
