from opengever.contact.interfaces import IContactSettings
from opengever.contact.service import ContactService
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.contact")


def contact_service():
    return ContactService()


def is_contact_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IContactSettings)
